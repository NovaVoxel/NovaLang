# ModulesList.nova
# Every Nova module implemented yet and what it does

`math.nova` (std/math)
    - sqrt(x: float) -> float
    - sin(x: float) -> float
    - cos(x: float) -> float
    - tan(x: float) -> float
    - log(x: float) -> float
    - exp(x: float) -> float

`random.nova` (std/random)
    - rand() -> int
    - rand_range(min: int, max: int) -> int

`io.nova` (std/io)
    - print(msg: str)
    - read_line() -> str

`net.nova` (std/net)
    - listen(host: str, port: int)
    - connect(host: str, port: int)
    - accept(server)
    - read(socket, bufsize: int = 4096) -> str
    - write(socket, data: str)
    - close(socket)

`gfx.nova` (std/gfx)
    - create_window(title: str, width: int, height: int)
    - clear(window, color: str = "black")
    - draw_rect(window, x: int, y: int, w: int, h: int, color: str = "white")
    - draw_text(window, text: str, x: int, y: int, color: str = "white")
    - run(window, loop_func)

`time.nova` (std/time)
    - now() -> str
    - sleep(ms: int)
    - timestamp() -> float

`fs.nova` (std/fs)
    - read_file(path: str) -> str
    - write_file(path: str, data: str)
    - list_dir(path: str) -> list

`cli.nova` (std/cli)
    - args() -> list
    - prompt(msg: str) -> str

`string.nova` (std/string)
    - split(s: str, sep: str) -> list
    - join(lst: list, sep: str) -> str
    - replace(s: str, old: str, new: str) -> str

`debug.nova` (std/debug)
    - assert(cond: bool, msg: str = "Assertion failed")
    - trace(obj)

`os.nova` (std/os)
    - getenv(key: str) -> str
    - setenv(key: str, value: str)
    - platform() -> str
    - cwd() -> str

`path.nova` (std/os.path)
    - join(a: str, b: str) -> str
    - basename(path: str) -> str
    - dirname(path: str) -> str
    - exists(path: str) -> bool

`hash.nova` (std/hash)
    - md5(data: str) -> str
    - sha256(data: str) -> str

`thread.nova` (std/thread)
    - spawn(func)
    - sleep(ms: int)
    - join(thread)

`http.nova` (std/http)
    - get(url: str) -> str
    - post(url: str, data: dict) -> str

`json.nova` (std/json)
    - parse(json_str: str) -> dict
    - stringify(obj: dict) -> str

`collections.nova` (std/collections)
    - list([...])
    - set([...])
    - map({key: value})
    - queue([...])

`re.nova` (std/re)
    - match(pattern: str, text: str)
    - search(pattern: str, text: str)
    - findall(pattern: str, text: str) -> list
    - sub(pattern: str, repl: str, text: str) -> str

`compiler.nova` (std/compiler)
    - read_source(path: str) -> str
    - parse(source: str)
    - generate_ir(ast)
    - codegen(ir, target: str) -> bytes
    - write_nomc(path: str, binary)
    - compile_file(src_path: str, out_path: str, target: str = "x86_64")

`errors.nova` (std/errors)
    - raise_error(msg: str)
    - format_error(err) -> str
    - log_error(msg: str)

`config.nova` (std/config)
    - load(path: str) -> dict
    - save(path: str, cfg: dict)
    - get(key: str, default=None)
    - set(key: str, value)
