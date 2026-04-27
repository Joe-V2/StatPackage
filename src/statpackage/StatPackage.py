from typing import List, Tuple, Dict
from threading import Lock

# Optionally set precision globally, e.g., getcontext().prec = 28

if __name__ == "__main__" :
    print("You're running this file wrong, pal! Implement it into a larger program to get started")
    exit(-1)

class StatPackage:
    """
    A package for statistical operations on time series data.
    
    This class provides methods for calculating moving averages, normalizing data,
    and other statistical operations using float for high precision arithmetic.
    Thread-safe operations are ensured using locks.
    """
    def __init__(self, base_data: List[float]):
        """
        Initialize the StatPackage with base data.
        
        Args:
            base_data: List of float values to perform statistical operations on
            
        Raises:
            ValueError: If base_data is empty
        """
        if len(base_data) <= 0:
            raise ValueError("Base data cannot be empty")
        self.data: List[float] = base_data
        self.averages: Dict[Tuple[int, int], List[float]] = {}
        self.lock = Lock()

    @property
    def total_items(self) -> int:
        return len(self.data)

    def trim(self, margin):
        self.data = self.data[:len(self.data) - margin]

    def calculate_moving_averages(self, period: int, base_data: List[float]) -> List[float]:
        """
        Calculate moving averages for the given data and period.
        
        Args:
            period: The period length for the moving average
            base_data: List of float values to calculate moving averages from
            
        Returns:
            List of float values representing the moving averages
            
        Raises:
            ValueError: If period is less than 1
        """
        if period < 1:
            raise ValueError("Period must be at least 1")
            
        result: List[float] = []
        for index in range(len(base_data)):
            start = index - period + 1
            end = index

            if end <= 0:
                average = float(base_data[end])
                result.append(average)
                continue

            average = result[index - 1]

            if start <= 0:
                average *= float(end)
                average += float(base_data[index])
                average /= float(end + 1)
                result.append(average)
                continue

            average -= base_data[start - 1] / float(period)
            average += base_data[end] / float(period)
            result.append(average)

        return result

    def get_original_value(self, index: int) -> float:
        return self.data[index]

    def get_moving_averages(self, period: int, order: int) -> List[float]:
        with self.lock:
            if order == -1:
                return self.data
            key = (period, order)
            if key in self.averages and self.averages[key] is not None:
                return self.averages[key]

            start_tuple = (period, 0)
            if start_tuple not in self.averages:
                self.averages[start_tuple] = self.calculate_moving_averages(period, self.data)

            for i in range(order):
                prev_tuple = (period, i)
                next_tuple = (period, i + 1)
                if next_tuple in self.averages and self.averages[next_tuple] is not None:
                    continue
                self.averages[next_tuple] = self.calculate_moving_averages(period, self.averages[prev_tuple])

            return self.averages[key]

    def get_moving_average_at_index(self, period: int, order: int, index: int) -> float:
        """
        Get the moving average at a specific index.
        
        Args:
            period: The period length for the moving average
            order: The order of the moving average
            index: The specific index to retrieve
            
        Returns:
            float representing the moving average value
            
        Raises:
            IndexError: If index is out of range
            ValueError: If period or order is less than -1
        """
        if period < 1:
            raise ValueError("Period must be at least 1")
        if order < -1:
            raise ValueError("Order must be more than -1")
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Index {index} out of range (0-{len(self.data)-1})")
            
        key = (period, order)
        if key not in self.averages:
            self.get_moving_averages(period, order)
        return self.averages[key][index]

    def get_number_required_for_moving_average_at_index(self, index: int, period: int, order: int, next_average: float) -> float:
        if(index > len(self.data)):
            raise IndexError("Index is out of range, this statpackage doesn't contain that much data!")

        if(period == 0):
            raise ValueError("Period cannot be 0, that's not how averages work!")

        if(order == -1):
            raise ValueError("Order cannot be -1, just reference this statpackage's base data indexes if you want that!")

        diff_required = 0.0
        for i in range(order, -1, -1):
            first_item_index = index - period
            diff_required *= float(period)

            prev_avg = self.get_moving_average_at_index(period, i, index - 1)
            divisor = float(period)

            if i == order:
                if i != 0:
                    diff_required = abs(next_average - (prev_avg - self.get_moving_average_at_index(period, i - 1, first_item_index) / divisor))
                else:
                    diff_required = abs(next_average - (prev_avg - self.data[first_item_index] / divisor))
                continue

            if i != 0:
                diff_required = abs(diff_required - (prev_avg - self.get_moving_average_at_index(period, i - 1, first_item_index) / divisor))
            else:
                diff_required = abs(diff_required - (prev_avg - self.data[first_item_index] / divisor))

        return diff_required * float(period)

    def get_elements_of_moving_average_at_index(self, period: int, order: int, index: int) -> List[float]:
        key = (period, order - 1)
        lowest_index_contributor = index - period + 1
        list_to_use = self.data if order == 0 else self.get_moving_averages(*key)

        result = [item for idx, item in enumerate(list_to_use) if lowest_index_contributor < idx <= index]

        if len(result) < period:
            result = [result[0]] * (period - len(result)) + result

        return result

    def get_preceding_elements_of_item_at_index(self, period: int, order: int, index: int) -> List[float]:
        return self.get_elements_of_moving_average_at_index(period, order + 1, index)[:period - 1]

    @staticmethod
    def normalise_data(data: List[float]) -> List[float]:
        return StatPackage.normalise_data_with_bounds(data, max(data), min(data))

    def denormalise_data(self, data: List[float], period : int(), order : int(), applyBaseline : bool() = True) -> List[float]:

        dataToUse = data if (period == 0 and order == 0) else self.get_moving_averages(period, order)

        highest = max(dataToUse)
        lowest = min(dataToUse)

        data = map((lambda x: x * (highest - lowest) + lowest if applyBaseline else x * (highest - lowest)), data)

        return list(data)


    @staticmethod
    def normalise_data_with_bounds(data: List[float], highest: float, lowest: float) -> List[float]:
        """
        Normalize data between 0 and 1 given custom highest and lowest bounds.
        
        Args:
            data: List of float values to normalize
            highest: Maximum value to use for normalization
            lowest: Minimum value to use for normalization
            
        Returns:
            List of normalized float values
        
        Raises:
            ValueError: If highest equals lowest (would cause division by zero)
        """
        if highest == lowest:
            raise ValueError("Cannot normalize: highest and lowest values are equal")
        return [(item - lowest) / (highest - lowest) for item in data]

    def get_deltas_per_index(self, base_data: List[float]) -> List[float]:
        result: List[float] = []
        for i in range(len(base_data)):
            if i == 0:
                result.append(float(0))
            else:
                result.append(base_data[i] - base_data[i - 1])
        return result
