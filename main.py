from playwright.sync_api import sync_playwright
import re

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

    horizontal_count = 0
    vertical_count = 0
    diagonal_count = 0

    # Create horizontal expressions
    for word in words:
        h_reverse = word[::-1]
        horizontal_exp = f"(?={word}|{h_reverse})"
        h_match = re.findall(horizontal_exp, grid)
        if h_match:
            horizontal_count += 1
            print(word)

    print("\n")

    # Create vertical expressions
    for word in words:
        v_forward = f".{{{width-1}}}".join(word)
        v_reverse = f".{{{width-1}}}".join(word[::-1])
        vertical_exp = f"(?={v_forward}|{v_reverse})"
        v_match = re.findall(vertical_exp, grid)
        if v_match:
            vertical_count += 1
            print(word)

    print("\n")

    # Create diagonal expressions
    for word in words:
        for n in [0, -2]:
            d_down = f".{{{width+n}}}".join(word)
            d_down_reverse = f".{{{width+n}}}".join(word[::-1])
            diagonal_expression = f"(?={d_down}|{d_down_reverse})"
            d_match = re.findall(diagonal_expression, grid)
            if d_match:
                diagonal_count += 1
                print(word)
                
    print("\n")

    # Check simple (horizontal/vertical) match count
    print(f"Horizontal matches: {horizontal_count} of {word_count}")
    print(f"Vertical matches: {vertical_count} of {word_count}")
    print(f"Total simple matches: {horizontal_count + vertical_count}, {int(((horizontal_count + vertical_count)/word_count)*100)}%")
    print(f"\nDiagonal matches: {diagonal_count}")
    print(f"Total words found: {horizontal_count + vertical_count + diagonal_count}")

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
