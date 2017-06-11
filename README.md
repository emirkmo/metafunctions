# MetaFunctions
[![Build Status](https://travis-ci.org/ForeverWintr/metafunctions.svg?branch=master)](https://travis-ci.org/ForeverWintr/metafunctions)

## Metafunctions is a function composition and data pipelining library. 
It allows for data pipeline creation separate from execution, so instead of writing:

```python
result = step3(step2(step1(data)))

#or
result_1 = step1(data)
result_2 = step2(result_1)
result_3 = step3(result_2)
```

You can write:

```python
pipeline = step1 | step2 | step3
result = pipeline(data)
```

### Why do you need new syntax for pipelining functions?
Well you may not *need* a new syntax, but the ability to compose a data pipeline before executing it does impart some advantages, such as:

* **Reuse**. Compose a pipeline once and use it in multiple places, including as part of larger pipelines:
  ```python
  # load, parse, clean, validate, and format are functions
  preprocess = load | parse | clean | validate | format
  
  # preprocess is now a MetaFunction, and can be reused
  clean_data1 = preprocess('path/to/data/file')
  clean_data2 = preprocess('path/to/different/file.')
  
  # Preprocess can be included in larger pipelines
  pipeline = preprocess | step1 | step2 | step3
  ```  
* **Readability**. `step1 | step2 | step3` is both read and executed from left to right, unlike `step3(step2(step1()))`, which is executed from innermost function outwards.
* **Inspection**. Can't remember what your MetaFunction does? `str` will tell you:
  ```python
  >>> str(preprocess)
  "(load | parse | clean | validate | format)"
* **Advanced Composition**. Anything beyond simple function chaining becomes difficult using traditional methods. What if you want to send the result of `step1` to both steps `2` and `3`, then sum the results? You'd traditionally have to write something like:
  ```python
  result1 = step1(data)
  result2 = step2(result1) + step3(result1)
  ```
  Which requires an intermediate variable and can quickly become unwieldy. Using metafunctions, you can declare a pipeline that does the same thing:
  ```python
  pipeline = step1 | step2 + step3
  result = pipeline(data)
  ```

## How does it work?

Conceptually, a MetaFunction is a function that contains other functions. When you call a MetaFunction, the MetaFunction calls the functions it contains. 

You can create a MetaFunction using the `node` decorator:
```python
from metafunctions.decorators import node

@node
def get_name(prompt):
    return input(prompt)

@node
def say_hello(name):
    return 'Hello {}!'.format(name)
```

MetaFunctions override certain operators to allow for composition. For example, the following creates a new MetaFunction that combines `get_name` and `say_hello`:
```python
greet = get_name | say_hello
```

When we call the `greet` MetaFunction, it calls both its internal functions in turn.
```python
# First, `get_name` is called, which prints our prompt to the screen.
# If we enter 'Tom' at the prompt, the second function returns the string 'Hello Tom!'
greeting = greet('Please enter your name ')
print(greeting) # Hello Tom!
```

MetaFunctions are also capable of upgrading regular functions to MetaFunctions at composition time, so we can simplify our example by composing `say_hello` directly with the builtin `input` and `print` functions:
```python
>>> greet = input | say_hello | print
>>> greet('Please enter your name: ')
# Please enter your name: Tom
# Hello tom!
```