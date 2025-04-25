from playwright.sync_api import sync_playwright
from datetime import datetime as dt
import re

def find_start_and_end_info(expression: str, grid: str, word: str, step: int) -> tuple:
    match = re.search(expression, grid)

    if match.group(1):
        start_index = match.start(1)
        end_index = start_index + (len(word) - 1) * step
    else:
        end_index = match.start(2)
        start_index = end_index + (len(word) - 1) * step

    start_coords = (start_index // width, start_index % width)
    end_coords = (end_index // width, end_index % width)

    return start_coords, end_coords

def find_page_elements_and_drag(start_coords: tuple, end_coords: tuple) -> None:
    start_row, start_col = start_coords
    end_row, end_col = end_coords

    start_box = rows.nth(start_row).locator('div[class="cell cell11"]').nth(start_col)
    end_box = rows.nth(end_row).locator('div[class="cell cell11"]').nth(end_col)

    start_box.drag_to(end_box)

puzzle_n = 5

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://api.razzlepuzzles.com/wordsearch")

    new_medium_game_button = page.locator("#newGameMedium")
    new_medium_game_button.click()

    timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

    for puzzle in range(puzzle_n):
        print(f"Starting puzzle {puzzle+1}...")

        word_elements = page.locator("#words .word.word-en.word-1")
        word_count = word_elements.count()
        words = [word_elements.nth(i).inner_text() for i in range(word_count)]

        grid_element = page.locator("#wordsearchGrid")
        rows = grid_element.locator('div[class="row row11"]')
        row_count = rows.count()
        lines = [rows.nth(t).inner_text().replace("\n", "") for t in range(row_count)]

        grid = "".join(lines)
        width = int(len(grid) ** (1/2))

        dir_config = {
            "Horizontal": {
                "step": 1,
                "expression": lambda word, width: f"({word})|({word[::-1]})",
            },
            "Vertical": {
                "step": width,
                "expression": lambda word, width: "("+f".{{{width-1}}}".join(word)+")|("+f".{{{width-1}}}".join(word[::-1])+")"
            },
            "Diagonal down right": {
                "step": width + 1,
                "expression": lambda word, width: "("+f".{{{width}}}".join(word)+")|("+f".{{{width}}}".join(word[::-1])+")"
            },
            "Diagonal down left": {
                "step": width - 1,
                "expression": lambda word, width: "("+f".{{{width-2}}}".join(word)+")|("+f".{{{width-2}}}".join(word[::-1])+")"
            },
        }

        direction_counts = {k: 0 for k in dir_config}

        for word in words:
            for dir, config in dir_config.items():
                expression = config["expression"](word, width)
                match = re.search(expression, grid)
                if match:
                    direction_counts[dir] += 1
                    step = config["step"]
                    start_coords, end_coords = find_start_and_end_info(expression, grid, word, step)
                    find_page_elements_and_drag(start_coords, end_coords)
                    break

        print("\n".join(f"{direction}: {count}" for direction, count in direction_counts.items()))

        grid_area = grid_element.bounding_box()
        word_area = page.locator("#words").bounding_box()

        x = min(grid_area["x"], word_area["x"]) - 25
        y = min(grid_area["y"], word_area["y"]) - 100
        right = max(grid_area["x"] + grid_area["width"], word_area["x"] + word_area["width"])
        bottom = max(grid_area["y"] + grid_area["height"], word_area["y"] + word_area["height"])
        screenshot_width = right - x
        screenshot_height = bottom - y

        page.screenshot(path=f"solves/{timestamp}_puzzle{puzzle+1}.png", clip={"x": x, "y": y, "width": screenshot_width+10, "height": screenshot_height})

        print(f"Completed and screenshotted puzzle {puzzle+1} of {puzzle_n}!\n")

        if puzzle < puzzle_n:
            new_game_button = page.locator("#endGameContent").locator("#newGameBtn")
            new_game_button.wait_for(state="attached")
            new_game_button.click()

            meta_close_button = page.locator("#metaPanel").locator("#metaClose")
            if meta_close_button.is_visible():
                meta_close_button.click()

            if new_medium_game_button:
                new_medium_game_button.click()

    browser.close()
