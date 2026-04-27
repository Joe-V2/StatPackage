# StatPackage - a Package for Moving Average Stats!
## What is this?
StatPackage is something I came up with whilst researching time-series data processing. Originally written in C#, this version was translated over to python using Claude.

A StatPackage isn't all that special in how it works, acting as a hashmap-style addressor for moving average components and derivatives. When precision matters however, I've found it pretty nifty to have on side... it's thread-safe too, allowing you to modify a single StatPackage object from wherever you like.

## What does it do?
A few things, really, but mostly focused on moving averages:
- Instantiate using StatPackage(List[float]) to initialise an object with some base "true" data.
- Get your moving averages using get_moving_averages, specifying a period and an order. Moving average sets are made as they are requested, so there's no need to worry about data that might not exist!
	- Periods are pretty basic, it's just how many entries previous to the current index contribute to the average at that index
	- Order is something I thought might be useful - it recursively iterates your averages, smoothing them out with fewer elements required. Think of it as something like a moving average of some moving averages.

There are some other fun things you can do, including finding what base, order-0 element would be required for a moving average at a given position, getting normalised moving average sets for machine learning, and getting all the elements of a given moving average from the most immediate contributing order. Take a look, get stuck in, and have fun!