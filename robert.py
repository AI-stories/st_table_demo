import os
from pathlib import Path

import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm


class Venue(BaseModel):
    city: str
    state: str
    country: str
    guest_capacity: int
    reception: bool
    ceremony: bool
    overnight_accommodations: bool
    catering_services: bool
    style: str


def main():
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    venue_data = []

    test_md_path = Path("test_md")
    if not test_md_path.exists():
        print(f"Warning: {test_md_path} directory not found")
        return

    md_files = list(test_md_path.glob("*.md"))
    for file in tqdm(md_files, desc="Processing venues", unit="file"):
        tqdm.write(f"Processing: {file.name}")

        with open(file, "r", encoding="utf-8") as f:
            md_content = f.read()

        venue_name = file.stem

        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the venue information. For string fields, use 'Unknown' if information is not available. For numerical fields, use -1 if information is not available.",
                    },
                    {
                        "role": "user",
                        "content": f"Extract venue information from this text about '{venue_name}':\n\n{md_content}",
                    },
                ],
                response_format=Venue,
            )

            venue = completion.choices[0].message.parsed
            venue_dict = venue.model_dump()
            venue_dict["name"] = venue_name
            venue_data.append(venue_dict)
            tqdm.write(f"✓ Successfully processed: {venue_name}")
        except Exception as e:
            tqdm.write(f"✗ Error processing {venue_name}: {e}")

    if venue_data:
        df = pd.DataFrame(venue_data)
        print(f"\nProcessed {len(venue_data)} venues")
        print(df)

        output_path = "venues_data.csv"
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    else:
        print("No venue data was processed")


if __name__ == "__main__":
    main()
