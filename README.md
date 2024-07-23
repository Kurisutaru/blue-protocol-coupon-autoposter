# Blue Protocol Coupon Auto-Poster

This project automates the process of posting coupon codes for Blue Protocol on supported sites using Selenium to simulate form filling. It supports major browsers like Firefox, Chrome, and Microsoft Edge, and runs on both Windows and Linux. Additionally, it can be run on demand or scheduled to run using cron jobs.

## Supported Sites
- [Game8.jp](https://game8.jp/)
- [H1g.jp](https://h1g.jp/)
- [Kamigame.jp](https://kamigame.jp/)
- [Gamerch.com](https://gamerch.com/)

## Features
- Automatic posting of coupon codes by simulating form submission
- Support for customizable templates using Python string formatting
- Runs on major browsers (Firefox, Chrome, Microsoft Edge)
- Compatible with Windows and Linux
- Can be run on demand or scheduled using cron jobs

## Requirements
- Python 3.x
- One of the supported browsers installed:
  - Firefox
  - Chrome
  - Microsoft Edge

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kurisutaru/blue-protocol-coupon-autoposter.git
   cd blue-protocol-coupon-autoposter
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure you have one of the supported browsers installed:**
   - [Google Chrome](https://www.google.com/chrome/)
   - [Mozilla Firefox](https://www.mozilla.org/firefox/new/)
   - [Microsoft Edge](https://www.microsoft.com/edge)

## Configuration

Rename `config.json.example` to `config.json`, or create a new `config.json` file in the root directory with the following structure:

```json
{
  "coupon": "ExampleCoupon123",
  "expired": "2024-12-31 23:59",
  "template": "{coupon} [{expired}]"
}
```

If you want to customize further, you can add additional fields like this:

```json
{
  "coupon": "ExampleCoupon123",
  "expired": "2024-12-31 23:59",
  "title": "ExampleTitle123",
  "template": "{coupon} {title} [{expired}]"
}
```

For more details on how to format the `template`, please refer to Python's string formatting documentation.

## Usage

Run the script on demand to automatically post the coupon code by simulating form submission. You need to specify the target website and the browser to use. Optionally, you can specify a custom browser path.

```bash
python main.py --game8 --chrome
```

### Arguments

Usage:
```plaintext
main.py [-h] (--game8 | --h1g | --kamigame | --gamerch) (--chrome | --firefox | --edge)
               [--custom-browser-location WHERE/YOU/INSTALL/THE/BROWSER]
```

- **Target Website (required):**
  - `--game8` for posting to [https://game8.jp/](https://game8.jp/)
  - `--h1g` for posting to [https://h1g.jp/](https://h1g.jp/)
  - `--kamigame` for posting to [https://kamigame.jp/](https://kamigame.jp/)
  - `--gamerch` for posting to [https://gamerch.com/](https://gamerch.com/)

- **Browser Selection (required):**
  - `--chrome` for using Google Chrome
  - `--firefox` for using Firefox
  - `--edge` for using Microsoft Edge

- **Custom Browser Path (optional):**
  - `--custom-browser-location` to specify the path to the custom browser binary (e.g., `WHERE/YOU/INSTALL/THE/BROWSER`)

## WebDriver

The WebDriver for the specified browser is automatically downloaded at runtime.

## Scheduling with Cron Jobs

To run the script automatically at specific intervals, you can set up a cron job (Linux) or Task Scheduler (Windows).

### Example Cron Job

Open your crontab editor:

```bash
crontab -e
```

Add the following line to run the script every day at midnight:

```bash
0 0 * * * /usr/bin/python3 /path/to/where/the/project/cloned/main.py --game8 --chrome
```

### Example Task Scheduler (Windows)

1. Open Task Scheduler.
2. Create a new task.
3. Set the trigger to your desired schedule.
4. Set the action to run the Python script with the appropriate interpreter.

## Contributing

Contributions are welcome! Please create a pull request or submit an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

The code for `tools.py` has been adapted from partial code in `SharedTools.py` and `WebDriverInstaller.py` from [ESET-KeyGen](https://github.com/rzc0d3r/ESET-KeyGen). Special thanks to the original authors for their contributions.