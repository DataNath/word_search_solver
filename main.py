from playwright.sync_api import sync_playwright
from datetime import datetime as dt
import re

def find_start_and_end_info(expression: str, grid: str, word: str, step: int, width: int) -> str:
    match = re.search(expression, grid)

    if match.group(1):
        start_index = match.start(1)
        end_index = start_index + (len(word) - 1) * step
    else:
        end_index = match.start(2)
        start_index = end_index + (len(word) - 1) * step

    start_coords = (start_index // width, start_index % width)
    end_coords = (end_index // width, end_index % width)

    # print(f"{word} found! Going from {start_coords} to {end_coords}.")
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

    for puzzle in range(puzzle_n):
        print(f"Starting puzzle {puzzle+1}...\n")

        word_elements = page.locator("#words .word.word-en.word-1")

        words = []

        for i in range(word_elements.count()):
            words.append(word_elements.nth(i).inner_text())

        word_count = len(words)

        grid_element = page.locator("#wordsearchGrid")

        rows = grid_element.locator('div[class="row row11"]')

        lines = []

        for t in range(rows.count()):
            lines.append(rows.nth(t).inner_text().replace("\n", ""))

        # Create grid as string and find width
        grid = "".join(lines)
        width = int(len(grid) ** (1/2))

        dir_map = {
            "h": 1,
            "v": width,
            "ddr": width + 1,
            "ddl": width - 1
        }

        h_count = 0
        v_count = 0
        d_count = 0

        # Create expressions
        for word in words:
            # Horizontal
            h_exp = f"({word})|({word[::-1]})"
            h_match = re.findall(h_exp, grid)
            if re.search(h_exp, grid):
                h_count += 1
                start_coords, end_coords = find_start_and_end_info(h_exp, grid, word, dir_map["h"], width)

            # Vertical
            v_f = f".{{{width-1}}}".join(word)
            v_r = f".{{{width-1}}}".join(word[::-1])
            v_exp = f"({v_f})|({v_r})"
            if re.search(v_exp, grid):
                v_count += 1
                start_coords, end_coords = find_start_and_end_info(v_exp, grid, word, dir_map["v"], width)

            # Diagonals
            for n in [0, -2]:
                d_f = f".{{{width+n}}}".join(word)
                d_r = f".{{{width+n}}}".join(word[::-1])
                d_exp = f"({d_f})|({d_r})"
                if re.search(d_exp, grid):
                    d_count += 1
                    start_coords, end_coords = find_start_and_end_info(d_exp, grid, word, dir_map["ddr" if n == 0 else "ddl"], width)

            find_page_elements_and_drag(start_coords, end_coords)

        print(f"Horizontal: {h_count}\nVertical: {v_count}\nDiagonal: {d_count}\n")

        timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

        grid_area = grid_element.bounding_box()
        word_area = page.locator("#words").bounding_box()

        x = min(grid_area["x"], word_area["x"]) - 25
        y = min(grid_area["y"], word_area["y"]) - 100
        right = max(grid_area["x"] + grid_area["width"], word_area["x"] + word_area["width"])
        bottom = max(grid_area["y"] + grid_area["height"], word_area["y"] + word_area["height"])
        width = right - x
        height = bottom - y

        page.screenshot(path=f"solves/solve_{timestamp}.png", clip={"x": x, "y": y, "width": width+10, "height": height})

        print(f"Completed and screenshotted puzzle {puzzle+1} of {puzzle_n}!\n")

        if puzzle < puzzle_n:
            new_game_button = page.locator("#endGameContent").locator("#newGameBtn")
            new_game_button.wait_for(state="attached")
            new_game_button.click()

            meta_close_button = page.locator("#metaClose")
            if meta_close_button.is_visible() and meta_close_button.is_enabled():
                meta_close_button.click()
                page.locator("#metaClose").click()

            if new_medium_game_button:
                new_medium_game_button.click()

    browser.close()
