import aiofile
from datetime import datetime
from colorist import Color, BrightColor, BgColor
import os
from typing import Callable, Literal

class LoggerBase:

    async def log(level: str, message: str, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass

    async def info(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass
    
    async def error(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass

    async def success(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass

    async def warning(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass

    async def debug(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        pass

class Logger(LoggerBase):
    def __init__(self, logger: LoggerBase, group: str = "logger", output: list[Literal["console", "file"]] = None):
        self.output = output
        self.logger = logger
        self.group = group

    async def info(self, message: any):
        await self.logger.info(str(message), group=self.group, output=self.output)
    
    async def error(self, message: any):
        await self.logger.error(str(message), group=self.group, output=self.output)

    async def success(self, message: any):
        await self.logger.success(str(message), group=self.group, output=self.output)

    async def warning(self, message: any):
        await self.logger.warning(str(message), group=self.group, output=self.output)

    async def debug(self, message: any):
        await self.logger.debug(str(message), group=self.group, output=self.output)

class logger(LoggerBase):

    foreground_colors = [
        BgColor.GREEN,
        BgColor.YELLOW,
        BgColor.MAGENTA,
        BgColor.CYAN,
        BgColor.BLUE,
    ]

    group_colors = {}

    paths: dict[str, str] = {}
    files: dict[str, aiofile.TextFileWrapper] = {}

    def getGroupColor(group: str):
        if group not in logger.group_colors:
            logger.group_colors[group] = logger.foreground_colors[len(logger.group_colors) % len(logger.foreground_colors)]
        return logger.group_colors[group]

    def config(path: str, 
            log_format: str = "{isoformat} {group} {level} {message}", 
            output: list[Literal["console", "file"]] = [ "console" ], 
            colorize: bool | dict[str, str] = True,
            wrapper: dict[str, Callable[[str], str]] = {}
            ):
        logger.dynamic_path = path
        logger.log_format = log_format
        logger.output = output
        if isinstance(colorize, bool):
            if colorize:
                logger.colorize = {
                    'INFO': BrightColor.BLACK,
                    'ERROR': Color.RED,
                    'WARNING': Color.YELLOW,
                    'DEBUG': Color.BLUE,
                    'SUCCESS': Color.GREEN
                }
            else:
                logger.colorize = None
        else:
            logger.colorize = colorize
        logger.start_time =  datetime.now()
        logger.is_path_group_dynamic = logger.dynamic_path.find('{group}') != -1
        logger.wrapper = wrapper

    def _get_format_data(group: str, level: str, time: datetime):
        data = {
            'isoformat': time.isoformat(),
            'datetime': time.strftime("%Y %m %d %H:%M:%S"),
            'safedate': time.strftime("%Y_%m_%d"),
            'daytime': time.strftime("%H:%M:%S"),
            'level': level,    
            'group': group
        }
        return data

    def _format_path(path: str, group: str, level: str, time: datetime):
        data = {
            **logger._get_format_data(group, level, time),
        }
        return time.strftime(path.format(**data))

    async def write_line(path: str, group: str, line: str):
        file_key = group if logger.is_path_group_dynamic else 'default'
        if file_key not in logger.paths or path != logger.paths[file_key]:
            directory = os.path.dirname(path)
            os.makedirs(directory, exist_ok=True)
            if not logger.is_path_group_dynamic and file_key in logger.files:
                await logger.files[file_key].close()
            logger.files[file_key] = await aiofile.async_open(path, 'a')
            logger.paths[file_key] = path
        await logger.files[file_key].write(line + '\n')
        await logger.files[file_key].flush()

    async def close():
        for _, file in logger.files.items():
            await file.close()


    def _wrap(type: str, value: str):
        if type in logger.wrapper:
            return logger.wrapper[type](value)
        return value

    def _format_log(data: dict[str, str], time: datetime):
        return time.strftime(logger.log_format.format(**data))

    def for_(group: str, output: list[Literal["console", "file"]] = None):
        return Logger(logger, group, output)

    async def log(level: str, message: str, group: str = "logger", output: list[Literal["console", "file"]] = None):
        if output is None:
            output = logger.output
        if output is None or len(output) == 0:
            raise ValueError("No output specified")
        lines = message.splitlines(keepends=False)
        now = datetime.now()
        path = logger._format_path(logger.dynamic_path, group, level, now)
        group_color = logger.getGroupColor(group)
        c_time = datetime.fromtimestamp(os.path.getctime(path)) if os.path.exists(path) else now
        elapsed = (now - c_time)
        elapsed = '{}.{:06}'.format(elapsed.seconds, elapsed.microseconds)
        level = logger._wrap('level', level)
        group = logger._wrap('group', group)
        for line in lines:
            data = {
                **logger._get_format_data(group, level, now),
                'elapsed': elapsed,
                'message': f'{"| " if len(lines) > 1 else ""}{line}'
            }
            isoformat = logger._wrap('isoformat', data['isoformat'])
            dt = logger._wrap('datetime', data['datetime'])
            if 'console' in output:
                if logger.colorize:
                    colored_data = {
                        **data,
                        'isoformat': f'{BrightColor.BLACK}{isoformat}{Color.OFF}',
                        'datetime': f'{BrightColor.BLACK}{dt}{Color.OFF}',
                        'level': f'{logger.colorize[level]}{level}{Color.OFF}',
                        'group': f'{Color.WHITE}{group_color}{group}{Color.OFF}',
                        'message': f'{logger.colorize[level]}{"| " if len(lines) > 1 else ""}{Color.OFF}{line}'
                    }
                    print(logger._format_log(colored_data, now))
                else:
                    print(logger._format_log(data, now))
            if 'file' in output:
                await logger.write_line(path, group, logger._format_log(data, now))

    async def info(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        await logger.log("INFO", str(message), group, output)
            
    async def error(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        await logger.log("ERROR", str(message), group, output)

    async def success(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        await logger.log("SUCCESS", str(message), group, output)

    async def warning(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        await logger.log("WARNING", str(message), group, output)

    async def debug(message: any, group: str = "logger", output: list[Literal["console", "file"]] = None):
        await logger.log("DEBUG", str(message), group, output)