"""
Campaign Audit Quiz — Session 8 final exam

In: campaigns_A.csv, plus the player's name and five quiz answers.
Process: read the raw CSV, clean the data, calculate CTR/CPA/ROAS, ask five
questions, check answers, calculate a score, and save the result.
Out: result.csv, containing the player's name, score, and date.
"""

import csv
from pathlib import Path
from datetime import date


# These are the files the program reads and writes.
DATA_FILE = "campaigns_A.csv"
RESULT_FILE = "result.csv"


def parse_euro_number(value):
    # The file uses a decimal comma, so turn values like "11088,60" into 11088.60.
    value = (value or "").strip()
    if value == "":
        return 0.0
    return float(value.replace(".", "").replace(",", "."))


def load_campaigns(filename):
    # Read a semicolon-separated CSV because the money values contain decimal commas.
    campaigns = []
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            # An empty impressions cell means this campaign must be excluded entirely.
            if not (row.get("Impressions") or "").strip():
                continue

            # Convert the text from the CSV into numbers we can calculate with.
            campaign = {
                "name": row["Campaign"].strip(),
                "channel": row["Channel"].strip(),
                "impressions": int(row["Impressions"]),
                "clicks": int(row["Clicks"]),
                "cost": parse_euro_number(row["Cost (€)"]),
                "conversions": int(row["Conversions"]),
                "revenue": parse_euro_number(row["Revenue (€)"]),
            }
            campaigns.append(campaign)

    return campaigns


def calculate_metrics(campaigns):
    # Calculate CTR and ROAS for each included campaign. A zero-conversion campaign
    # has no CPA, so CPA is stored as None instead of dividing by zero.
    for campaign in campaigns:
        campaign["ctr"] = campaign["clicks"] / campaign["impressions"] * 100

        if campaign["conversions"] == 0:
            campaign["cpa"] = None
        else:
            campaign["cpa"] = campaign["cost"] / campaign["conversions"]

        if campaign["cost"] == 0:
            campaign["roas"] = None
        else:
            campaign["roas"] = campaign["revenue"] / campaign["cost"]

    return campaigns


def get_answers(campaigns):
    # Work out the correct answers from the data rather than hard-coding them.
    best_ctr = max(campaigns, key=lambda campaign: campaign["ctr"])
    campaigns_with_cpa = [
        campaign for campaign in campaigns if campaign["cpa"] is not None
    ]
    highest_cpa = max(campaigns_with_cpa, key=lambda campaign: campaign["cpa"])
    roas_above_three = sum(
        1 for campaign in campaigns
        if campaign["roas"] is not None and campaign["roas"] > 3
    )

    # Add conversions together by channel to find the channel with most conversions.
    conversions_by_channel = {}
    for campaign in campaigns:
        channel = campaign["channel"]
        conversions_by_channel[channel] = (
            conversions_by_channel.get(channel, 0) + campaign["conversions"]
        )
    best_channel = max(conversions_by_channel, key=conversions_by_channel.get)

    average_ctr = sum(campaign["ctr"] for campaign in campaigns) / len(campaigns)

    return [
        best_ctr["name"],
        highest_cpa["name"],
        str(roas_above_three),
        best_channel,
        f"{average_ctr:.2f}",
    ]


def ask_and_score(answers):
    # Ask for the player's name, then ask five questions and award one point per answer.
    player_name = input("Your name: ").strip()
    if not player_name:
        player_name = "Anonymous"

    questions = [
        "1) Which campaign has the best CTR? Enter its campaign name: ",
        "2) Which campaign has the highest CPA? Enter its campaign name: ",
        "3) How many campaigns have a ROAS above 3? Enter a whole number: ",
        "4) Which channel generated the most conversions in total? Enter the channel: ",
        "5) What is the average CTR across all included campaigns, rounded to 2 decimals? ",
    ]

    score = 0
    for question, correct_answer in zip(questions, answers):
        response = input(question).strip()

        # Compare names without worrying about capitalization or extra spaces.
        if correct_answer in (answers[0], answers[1], answers[3]):
            is_correct = response.casefold() == correct_answer.casefold()
        elif correct_answer == answers[2]:
            is_correct = response == correct_answer
        else:
            # Allow 2.6 and 2.60 as the same average CTR answer.
            try:
                is_correct = abs(float(response.replace(",", ".")) - float(correct_answer)) < 0.005
            except ValueError:
                is_correct = False

        if is_correct:
            print("Correct!")
            score += 1
        else:
            print("Not quite. The correct answer is:", correct_answer)

    print(f"Final score: {score}/5")
    return player_name, score


def save_result(player_name, score, filename):
    # Add a result row. Write the header only for a new or empty result file.
    path = Path(filename)
    needs_header = not path.exists() or path.stat().st_size == 0

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if needs_header:
            writer.writerow(["player_name", "score", "date"])
        writer.writerow([player_name, f"{score}/5", date.today().isoformat()])


def main():
    # Run the whole quiz in order and give a helpful message if a file is missing or malformed.
    try:
        campaigns = load_campaigns(DATA_FILE)
        if not campaigns:
            print("No campaigns with valid impressions were found.")
            return

        calculate_metrics(campaigns)
        print(f"Loaded {len(campaigns)} campaigns after excluding rows with blank impressions.")
        answers = get_answers(campaigns)
        player_name, score = ask_and_score(answers)
        save_result(player_name, score, RESULT_FILE)
        print("Your result was saved to", RESULT_FILE)

    except FileNotFoundError as error:
        print("File not found:", error)
        print("Keep campaigns_A.csv in the same folder as this program.")
    except (KeyError, ValueError, ZeroDivisionError) as error:
        print("There is a problem with the CSV data:", error)
        print("Check the column names and numeric values in campaigns_A.csv.")


if __name__ == "__main__":
    main()
