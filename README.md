# asynclogger

A lightweight and efficient asynchronous logging package for logging messages to the console and files. Supports colored output, dynamic log paths, and customizable log levels.

## Features

- **Asynchronous Logging**: Non-blocking logging for improved performance.
- **Console and File Logging**: Supports simultaneous logging to console and files.
- **Colored Output**: Differentiates log levels using colors for better readability.
- **Dynamic Log Paths**: Change log file paths dynamically without restarting.
- **Custom Log Levels**: Define and configure custom logging levels.

## Installation

```sh
pip install asynclogger
```

## Usage

### Basic Example

```python
from asynclogger import logger

logger.config('./logs/test.log', log_to_console=True)

async def main():
    await logger.info('Hello, world!')

if __name__ == '__main__':
    asyncio.run(main())

```

### Configuration Options

| Option         | Type    | Default         | Description |
|----------------|--------|---------------|-------------|
| `log_format`  | String | `{isoformat} {group} {level} {message}` | Format used for logging messages. |
| `output` | List | `["console"]` | Specifies outputs. |
| `colorize`  | Boolean or Dict | `True` | Takes either a boolean or a dict specifying a color for each log level. |
| `wrapper`     | Dict | `{}` | Contains a dict of wrapper functions for each format variable (isoformat, group, level ...). |

### Dynamic Log Path Change

```python
logger.config('./logs/%Y/%B/{safedate}.log', log_to_console=True)
```

### Custom Log Levels

```python
await logger.log('custom', 'This is a custom log level message')
```

### Coloring Output

```python
from colorist import Color

logger.config('./logs/test.log', log_to_console=True, colorize={
    'ERROR': Color.GREEN
})
```

### Wrapping Variables

```python
logger.config('./logs/test.log', log_to_console=True, wrapper={'group': lambda x: f'({x})'})
```

## License

MIT

