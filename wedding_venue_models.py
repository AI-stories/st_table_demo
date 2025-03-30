from typing import Literal

from pydantic import BaseModel, Field


class WeddingContactInfo(BaseModel):
    city: str | None = Field(description="The city this wedding venue is located in.")
    state: str | None = Field(description="The state this wedding venue is located in.")
    zip_code: str | None = Field(
        description="The zip code this wedding venue is located in."
    )
    country: str | None = Field(
        description="The country this wedding venue is located in."
    )
    email: str | None = Field(description="The email address of the wedding venue.")
    phone: str | None = Field(description="The phone number of the wedding venue.")
    website: str | None = Field(description="The website of the wedding venue.")


class MenuBreakdown(BaseModel):
    appetizers: str | None = Field(
        description="List of specific appetizer options offered (e.g., 'bruschetta, shrimp cocktail'). Return null if not specified."
    )
    main_courses: str | None = Field(
        description="List of specific main course options offered (e.g., 'chicken, salmon, vegetarian pasta'). Return null if not specified."
    )
    desserts: str | None = Field(
        description="List of specific dessert options offered (e.g., 'chocolate cake, fruit tart'). Return null if not specified."
    )
    dietary_accommodations: str | None = Field(
        description="Details on dietary accommodations available (e.g., 'gluten-free, vegan options'). Return null if not specified."
    )
    assumptions: str | None = Field(
        description="Key assumptions made about the menu (e.g., '100 guests, middle-tier package'). Return null if not specified."
    )
    cost_options: str | None = Field(
        description="Options or factors contributing to the overall food cost (e.g., '$50 per person for premium menu'). Return null if not specified."
    )


class BarBreakdown(BaseModel):
    wines: str | None = Field(
        description="List of specific wine options offered (e.g., 'Cabernet Sauvignon, Chardonnay'). Return null if not specified."
    )
    cocktails: str | None = Field(
        description="List of specific cocktail options offered (e.g., 'Margarita, Mojito'). Return null if not specified."
    )
    spirits: str | None = Field(
        description="List of specific spirit options offered (e.g., 'Vodka, Whiskey'). Return null if not specified."
    )
    non_alcoholic: str | None = Field(
        description="List of specific non-alcoholic options offered (e.g., 'Soda, Juice'). Return null if not specified."
    )
    assumptions: str | None = Field(
        description="Key assumptions made about the bar (e.g., '100 guests, 3-hour open bar'). Return null if not specified."
    )
    cost_options: str | None = Field(
        description="Options or factors contributing to the overall bar cost (e.g., '$20 per person for open bar'). Return null if not specified."
    )


class WeddingFoodInfo(BaseModel):
    menu_breakdown: MenuBreakdown | None = Field(
        description="Provide a structured breakdown of the food options at the venue. Include appetizers, main courses, desserts, dietary accommodations, key assumptions, and options that contribute to the overall cost. Return a detailed breakdown using the MenuBreakdown model."
    )
    bar_breakdown: BarBreakdown | None = Field(
        description="Provide a structured breakdown of the bar and alcohol options at the venue. Return a detailed breakdown using the BarBreakdown model."
    )
    outside_food_allowed: bool | None = Field(
        description="Can external catering or food vendors be used at this venue?If the text explicitely mentions allowing outside catering or food vendors, answer True. Do not consider desserts or cakes as food, as these are different categories. If not mentioned, default to False."
    )
    outside_alcohol_allowed: bool | None = Field(
        description="Can external alcohol be brought into this venue?If the text mentions the venue has a liquor license or provides alcohol service, answer False. If the text explicitly mentions allowing outside alcohol or BYOB policy, answer True. If not mentioned, default to False."
    )
    outside_dessert_allowed: bool | None = Field(
        description="Can external desserts or cakes be brought into this venue?If the text explicitly mentions allowing outside desserts or cakes, answer True. If not mentioned, default to True."
    )
    kosher_food: bool | None = Field(
        description="Does the venue offer certified kosher menu options, either in-house or through external vendors?Answer True ONLY if kosher options are explicitly mentioned or if the venue explicitly states they accommodate religious dietary restrictions. If not mentioned, default to False."
    )
    halal_food: bool | None = Field(
        description="Does the venue offer certified halal menu options, either in-house or through external vendors? Return True if offered, False if not offered. Answer True ONLY if halal options are explicitly mentioned. If not mentioned, default to False."
    )
    east_asian_food: bool | None = Field(
        description="Does the venue offer East Asian food options (Chinese, Japanese, Korean, etc.), either in-house or through external vendors? Answer True if East Asian cuisine is explicitly mentioned or if the venue offers international cuisine. If not mentioned, default to False."
    )
    indian_food: bool | None = Field(
        description="Does the venue offer Indian food options, either in-house or through external vendors? Answer True if Indian cuisine is explicitly mentioned or if the venue offers diverse international cuisine that likely includes Indian options. If not mentioned, default to False."
    )
    gluten_free_food: bool | None = Field(
        description="Does the venue offer gluten-free food options? Return True if offered, False if not offered. Answer True if gluten-free options are explicitly mentioned. If the venue mentions accommodating dietary restrictions/allergies/food preferences, return True."
    )
    other_ethnic_food_style: str | None = Field(
        description="Does the venue offer other ethnic food styles beyond those already mentioned? If so, list the available styles as a comma-separated string. If no other ethnic food styles are mentioned, return None."
    )
    late_night_food: bool | None = Field(
        description="Does the venue provide late-night food options, such as pizza or snacks after dinner and dessert service? If not mentioned, default to False."
    )
    name: str


class PriceBreakdown(BaseModel):
    base_prices: str | None = Field(
        description="The base cost of the venue, including any variations based on day of the week or package (e.g., '$20,000 Sunday for 80 guests, $26,000 Friday/Saturday for 80 guests, $150 per extra guest')."
    )
    total_cost_for_assumed_guest_count: str | None = Field(
        description="The total cost for an assumed guest count, before taxes and fees, specifying the guest count and day (e.g., '100 guests on a Sunday, $23,000')."
    )
    taxes_and_fees: str | None = Field(
        description="The breakdown of taxes, gratuity, and any additional fees, including their individual amounts and the total (e.g., '9.5% tax at $2,185, 20% gratuity at $4,600, 6% healthcare fee at $1,380, 5.5% admin fee at $1,265, total $9,430')."
    )
    per_person_cost: str | None = Field(
        description="The per-person cost after taxes, fees, and gratuity for the assumed guest count (e.g., '$324 after taxes and fees for 100 guests')."
    )
    inclusions: str | None = Field(
        description="Items included in the price, such as specific menu items, beverages, or services (e.g., 'private use of San Vicente Room, Green Room, and Main Room, specialty menu with food stations and tray-passed hors d'oeuvres like bacon-wrapped dates, beverages including sommelier-selected wines, specialty cocktails like Green Goddess, select-spirit open bar with Tito's vodka')."
    )
    exclusions: str | None = Field(
        description="Items not included in the price that may incur additional costs (e.g., 'dance floor and insurance costs unspecified, optional parking validation at $19 per car, photography assumed but not specified')."
    )
    assumptions: str | None = Field(
        description="Key assumptions made in the cost calculation, such as guest count, day of the week, or gratuity rate (e.g., '100 guests, Sunday pricing as middle option, 20% gratuity as midpoint')."
    )


class WeddingPriceInfo(BaseModel):
    option: Literal["deluxe", "premium", "standard", "economy", "other"]
    """
    This is the pricing option for this wedding venue.
    """
    price: int
    """
    This is the price for this wedding venue.
    """
    summary: str
    """
    This is a summary of the package option for this wedding venue.
    """
    price_breakdown: PriceBreakdown
    """
    This is the breakdown of the price for this wedding venue.
    """


class WeddingVenuePricingSummary(BaseModel):
    options: list[WeddingPriceInfo]
    """
    This is a list of all the pricing options for this wedding venue.
    """


class WeddingPriceInfo(BaseModel):
    price: int | None = Field(
        description="Give me your best guess for the cost per person it would be to have a wedding reception at this venue. Respond with only a number. Treat the costs associated with the ceremony as separate. If there are unknowns, use your best judgment to guesstimate the cost given the geographic location and relative 'niceness' of the property. If there are multiple packages and options, choose the middle or medium option to provide the best reference point. When you give the number,make sure you account for local taxes, tip, and any service charges. Assume that couples will pay for standard things like dinner, an appetizer course, dessert, alcohol, photography but exclude non-standard things like a late-night meal."
    )
    price_breakdown: PriceBreakdown | None = Field(
        description="Provide a structured breakdown of the pricing for this venue, with each category as a separate field. Include the base cost, per-person cost for additional guests, total cost for an assumed guest count (state the count), and per-person cost after taxes, fees, and gratuity. List all inclusions (e.g., specific menu items like food stations or cocktail names, beverage details) and exclusions (e.g., dance floor, insurance). Detail key assumptions (e.g., day of week, guest count) and options contributing to the cost."
    )
    ceremony_cost: int | None = Field(
        description="Estimate a cost for the ceremony. Respond with a number only which would be your best guess based on the available information. Use -1 if no information is provided."
    )
    pricing_transparency: (
        Literal[
            "This venue discloses a small portion of the total wedding costs",
            "This venue discloses a moderate portion of the total wedding costs",
            "This venue discloses a high degree of the total costs",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="""Assess how much of the total wedding cost is disclosed in the provided materials. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value: \n  - This venue discloses a small portion of the total wedding costs.\n  - This venue discloses a moderate portion of the total wedding costs.\n  - This venue discloses a high degree of the total wedding costs\n  - Not enough information. 
        \n Guidance when selecting the option: A 'small portion' of disclosure means significant costs (e.g., food, bar/alcohol) are unclear or require contacting external vendors. A 'moderate portion' means some unknowns exist, but you can get a general cost idea without much extra work. A 'high degree' means most costs are disclosed with few surprises, little additional work needed to understand the total cost."""
    )
    deposit_and_payment_plans: (
        Literal[
            "The venue works with me on deposit terms and payment plans",
            "The venue does not have flexibility on deposit terms and payment plans",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="""Determine if the venue offers flexibility on deposit terms and payment plans. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value: \n  - The venue works with me on deposit terms and payment plans\n  - The venue does not have flexibility on deposit terms and payment plans\n  - Not enough information. 
        \n Follow these guidance when selecting the option: Flexibility means the venue allows negotiation on deposit amounts, payment schedules, or offers installment plans. Lack of flexibility is indicated by strict terms or no mention of flexible options."""
    )


class WeddingVenueOther(BaseModel):
    outside_wedding_coordinator: bool | None = Field(
        description="This venue lets me bring in my own wedding coordinator"
    )
    outside_photographer: bool | None = Field(
        description="This venue lets me bring in my own photographer"
    )
    package_approach: (
        Literal[
            "This venue offers fixed packages, with a few extras or options",
            "This venue offers a moderate or flexible approach",
            "This venue provides a high degree of flexibility",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="""Determine the wedding package approach of the venue. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s description as the field value: \n  - This venue offers fixed packages, with a few extras or options\n  - This venue offers a moderate or flexible approach\n  - This venue provides a high degree of flexibility\n  - Not enough information. 
        \n For guidance: Fixed packages include in-house services (e.g., pre-set menus); moderate offers a mix; high flexibility requires client planning."""
    )
    reception_or_ceremony: (
        Literal[
            "Only space for reception",
            "Only space for the ceremony",
            "Both reception and the ceremony space",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="Determine an option for spaces provided by the venue. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s description as the field value: \n  - Only space for reception\n  - Only space for the ceremony\n  - Both reception and the ceremony space\n  - Not enough information."
    )
    what_time_does_the_party_need_to_stop: (
        Literal[
            "10PM",
            "12AM",
            "After 12AM",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="Determine the latest time the event must conclude. You MUST CHOOSE ONE of the following options that best matches the document’s content: \n  - 10PM\n  - 12AM\n  - After 12AM\n  - Not enough information."
    )
    top_choices: str | None = Field(
        description="Give me 1-2 reasons why you think a client is most likely to choose this venue (e.g., what are the biggest key selling points or benefits)."
    )
    guest_capacity: Literal[1, 50, 100, 150, 200, 300] | None = Field(
        description="Determine the estimated guest capacity. You MUST CHOOSE ONE of the following approximate maximums that best matches the document’s content, representing the upper bound of each range: \n  - 1 (for 1-50)\n  - 50 (for 50-100)\n  - 100 (for 100-150)\n  - 150 (for 150-200)\n  - 200 (for 200-300)\n  - 300 (for 300+). Guidance: Infer from max guests or room size (e.g., 'up to 150 guests' = 150)."
    )


class WeddingVenueStyle(BaseModel):
    style: (
        Literal[
            "Barns & Farms",
            "Hotels",
            "Winery",
            "Country Clubs",
            "Restaurants",
            "Rooftops & Lofts",
            "Mansions",
            "Religious Spaces",
            "Museums",
            "Boats",
            "Parks",
            "Historic Venues",
            "Banquet Halls",
            "Beach",
            "Garden",
            "Waterfront",
            "Brewery",
            "State",
            "Local",
            "Government Property",
            "Other",
        ]
        | None
    ) = Field(
        description="Determine the style of the venue. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s value as the field value: \n  - Barns & Farms\n  - Hotels\n  - Winery\n  - Country Clubs\n  - Restaurants\n  - Rooftops & Lofts\n  - Mansions\n  - Religious Spaces\n  - Museums\n  - Boats\n  - Parks\n  - Historic Venues\n  - Banquet Halls\n  - Beach\n  - Garden\n  - Waterfront\n  - Brewery\n  - State\n  - Local\n  - Government Property\n  - Other"
    )
    indoor_outdoor: (
        Literal[
            "Outdoor space but has a covering to provide some protection against weather elements",
            "Predominantly outdoor",
            "Predominantly without protection",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="Determine the indoor/outdoor nature of the venue. You MUST CHOOSE ONE of the following options and return the selected option’s description as the field value: \n  - Outdoor space but has a covering to provide some protection against weather elements\n  - Predominantly outdoor\n  - Predominantly without protection\n  - Not enough information. For guidance: You must choose one of the above options. A predominantly outdoor space may include gardens or patios, while one without a covering lacks weather protection (e.g., an open field)."
    )
    privacy: (
        Literal[
            "Privacy and exclusivity is a major feature of the venue",
            "Moderate privacy with possible nearby non-wedding guests",
            "Shared or public space",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="Assess the privacy level. You MUST CHOOSE ONE of the following options and return the selected option’s description as the field value: \n  - Privacy and exclusivity is a major feature of the venue\n  - Moderate privacy with possible nearby non-wedding guests\n  - Shared or public space\n  - Not enough information."
    )
    accommodations: (
        Literal[
            "On-site lodging accommodations or extremely close (less than 5 mins walking distance) is possible",
            "No On-site lodging, third-party 5-10 minutes away.",
            "No on-site lodging, third-party 10+ minutes away.",
            "Not enough information",
        ]
        | None
    ) = Field(
        description="Determine the lodging accommodations offered by the venue. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s description as the field value: \n  - On-site lodging accommodations or extremely close (less than 5 mins walking distance) is possible\n  - No On-site lodging, third-party 5-10 minutes away.\n  - No on-site lodging, third-party 10+ minutes away.\n  - Not enough information."
    )
    environmental: (
        Literal[
            "This venue focuses on minimal environmental impact and sustainability in their offering",
            "This venue does not emphasize environment or sustainability",
        ]
        | None
    ) = Field(
        description="Assess the venue’s emphasis on environmental sustainability. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s description as the field value: \n  - This venue focuses on minimal environmental impact and sustainability in their offering\n  - This venue does not emphasize environment or sustainability. \n For guidance: A focus on sustainability might include eco-friendly practices (e.g., local sourcing or renewable energy), while lack of emphasis implies no mention of such efforts."
    )
    general_vibe: (
        Literal[
            "Rustic and simple",
            "Peaceful and serene",
            "Grandiose and elegant",
            "Adventurous or quirky",
            "Warm and cozy",
            "Other",
        ]
        | None
    ) = Field(
        description="Determine the general vibe or atmosphere of the venue. You MUST CHOOSE ONE of the following options that best matches the document’s content and return the selected option’s description as the field value: \n  - Rustic and simple\n  - Peaceful and serene\n  - Grandiose and elegant\n  - Adventurous or quirky\n  - Warm and cozy\n  - Other. For guidance: Rustic and simple might include barns or farms, peaceful and serene could be gardens, grandiose and elegant might be mansions, adventurous or quirky could involve unique spaces, and warm and cozy might be cozy interiors."
    )
