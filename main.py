from playwright.sync_api import sync_playwright
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

    print(f"{word} found! Going from {start_coords} to {end_coords}.")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://api.razzlepuzzles.com/wordsearch")

    new_medium_game_button = page.locator("#newGameMedium")
    new_medium_game_button.click()

    # # Force fresh game
    # menu_button = page.locator('div[class="menuIconCon"]')
    # menu_button.click()

    # new_game = page.get_by_text("New Game")
    # new_game.click()

    # new_medium_game_button.click()

    word_elements = page.locator("#words .word.word-en.word-1")

    words = []

    for i in range(word_elements.count()):
        words.append(word_elements.nth(i).inner_text())

    word_count = len(words)

    grid = page.locator("#wordsearchGrid")

    rows = grid.locator('div[class="row row11"]')

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
            find_start_and_end_info(h_exp, grid, word, dir_map["h"], width)

        # Vertical
        v_f = f".{{{width-1}}}".join(word)
        v_r = f".{{{width-1}}}".join(word[::-1])
        v_exp = f"({v_f})|({v_r})"
        if re.search(v_exp, grid):
            v_count += 1
            find_start_and_end_info(v_exp, grid, word, dir_map["v"], width)

        # Diagonals
        for n in [0, -2]:
            d_f = f".{{{width+n}}}".join(word)
            d_r = f".{{{width+n}}}".join(word[::-1])
            d_exp = f"({d_f})|({d_r})"
            if re.search(d_exp, grid):
                d_count += 1
                find_start_and_end_info(d_exp, grid, word, dir_map["ddr" if n == 0 else "ddl"], width)
    
    print(f"Horizontal: {h_count}\nVertical: {v_count}\nDiagonal: {d_count}")
    print(f"Total words found: {h_count + v_count + d_count}")

    # row_dict = {}

    # for r in range(rows.count()):
    #     row = rows.nth(r).inner_text().split()
    #     row_dict[r+1] = row

    # grid_pos = {}

    # for row, letters in row_dict.items():
    #     for index, letter in enumerate(letters, start=1):
    #         grid_pos[(row, index)] = letter

    # for coord, letter in grid_pos.items():
    #     print(f"Coordinates {coord}: {letter}")

    input("Press ENTER to close the browser...")

    browser.close()
