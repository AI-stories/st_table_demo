from typing import Literal

from pydantic import BaseModel, Field

TierName = Literal["Standard", "Signature", "Premium"]


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
    facebook: str | None = Field(description="The facebook page of the wedding venue.")
    instagram: str | None = Field(
        description="The instagram account of the wedding venue."
    )


class MenuTier(BaseModel):
    name: TierName = Field(
        description="Tier name: must be Standard, Signature, or Premium."
    )
    appetizers: str | None = Field(description="Appetizers in this tier.")
    entrees: str | None = Field(description="Entrées in this tier.")
    sides: str | None = Field(description="Side dishes in this tier.")
    desserts: str | None = Field(description="Desserts in this tier.")
    beverages: str | None = Field(description="Beverages in this tier.")

    def to_string(self) -> str:
        parts = [f"{self.name}"]
        if self.appetizers:
            parts.append(f"- Appetizers: {self.appetizers}")
        if self.entrees:
            parts.append(f"- Entrées: {self.entrees}")
        if self.sides:
            parts.append(f"- Sides: {self.sides}")
        if self.desserts:
            parts.append(f"- Desserts: {self.desserts}")
        if self.beverages:
            parts.append(f"- Beverages: {self.beverages}")
        if len(parts) == 1:
            return ""
        return "\n".join(parts)


class FoodBreakdown(BaseModel):
    """
    You must return exactly three food tiers: Standard, Signature, and
    Premium.

    Venues often name their packages arbitrarily (e.g., "Adore", "Silver",
    "Classic", "Treasure"). Your task is to interpret these names and map each one
    to a standard tier by evaluating the **menu quality, service level, and
    pricing**.

    Use the following general guidance:

    - **Standard**: basic offerings, lower price point
    - **Signature**: moderate enhancements, mid-range price
    - **Premium**: multiple high-end appetizers, upgraded entrées (beef,
        seafood), top-tier service, highest price

    Ignore the original package names. Focus only on the **content and price range**
    to assign the correct standard tier name.
    """

    tiers: list[MenuTier] = Field(
        description="List of exactly 3 tiers: Standard (Silver), Signature (Gold), Premium (Platinum)."
    )
    flexibility: Literal[
        "0: Completely fixed packages, no flexibility",
        "1: Fixed packages with a few extras or options",
        "2: Moderate or flexible approach",
        "3: Highly customizable with some structure",
        "4: Completely custom/DIY",
    ] = Field(
        description="How much freedom does the customer have to customize the food-related tier packages?"
    )

    def to_string(self) -> str:
        return "\n\n".join([tier.to_string() for tier in self.tiers])


class BarTier(BaseModel):
    name: TierName = Field(
        description="Tier name: must be Standard, Signature, or Premium."
    )
    highlights: str | None = Field(
        description="Beverages and package highlights in this drink package."
    )

    bar_pricing_model: Literal["Open bar", "Hosted bar", "Cash bar", "Not Offered"] = (
        Field(
            description="""- open bar: the venue provides the bar and the drinks, prepaid for by the host
- hosted bar: the venue provides the bar and the drinks, paid for by the host at the end of the night, also referred to as a consumption bar or tab bar
- cash bar: the venue provides the bar, but the drinks are payed for by the guests
- not offered: the venue does not offer a bar or is not specified"""
        )
    )

    def to_string(self) -> str:
        parts = [f"{self.name}"]
        if self.highlights:
            parts.append(f"- Highlights: {self.highlights}")
        if self.bar_pricing_model != "Not Offered":
            parts.append(f"- Bar Pricing Model: {self.bar_pricing_model}")
        return "\n".join(parts)


class BarBreakdown(BaseModel):
    """
    You must return exactly three bar tiers: Standard, Signature, and
    Premium.

    Many venues use unique names for their drink packages. Instead of
    copying those names, evaluate the **included alcohol types and
    service level**, and map them to a standard tier:

    - **Standard**: basic offerings, lower price point
    - **Signature**: mid-range price, includes house liquors or a soft
        bar with wine service
    - **Premium**: top-tier service, highest price like top-shelf
        liquor, signature cocktails, champagne toast, or full open bar

    Always normalize to these three tiers based on the drink offerings —
    not the label.
    """

    tiers: list[BarTier] = Field(
        description="List of exactly 3 tiers: Standard (Silver), Signature (Gold), Premium (Platinum)."
    )
    flexibility: Literal[
        "0: Completely fixed packages, no flexibility",
        "1: Fixed packages with a few extras or options",
        "2: Moderate or flexible approach",
        "3: Highly customizable with some structure",
        "4: Completely custom/DIY",
    ] = Field(
        description="How much freedom does the customer have to customize the package?"
    )

    def to_string(self) -> str:
        parts = []
        for tier in self.tiers:
            parts.append(tier.to_string())

        return "\n".join(parts)


class WeddingPriceInfo(BaseModel):
    option: Literal["standard", "premium", "signature"] = Field(
        description="This is the pricing option for this wedding venue."
    )
    ceremony_cost: int | Literal["unknown"] = Field(
        description="Estimate a cost for the ceremony. Respond with a number only which would be your best guess based on the available information. Use 'unknown' if no information is provided."
    )

    def to_string(self) -> str:
        if self.ceremony_cost:
            return f"Ceremony: {self.option}\n - ceremony cost: ${self.ceremony_cost}\n"
        return ""


class WeddingVenueStyle(BaseModel):
    style: Literal[
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
    ] = Field(
        description="""Determine the style of the venue. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's value as the field value:
- Barns & Farms
- Hotels
- Winery
- Country Clubs
- Restaurants
- Rooftops & Lofts
- Mansions
- Religious Spaces
- Museums
- Boats
- Parks
- Historic Venues
- Banquet Halls
- Beach
- Garden
- Waterfront
- Brewery
- State
- Local
- Government Property
- Other"""
    )
    indoor_outdoor: Literal[
        "1: Completely indoor",
        "2: Predominantly indoor",
        "3: Equal indoor/outdoor mix",
        "4: Predominantly outdoor",
        "5: Completely outdoor",
        "X: Not enough information",
    ] = Field(
        description="""Determine the indoor/outdoor nature of the venue. You MUST CHOOSE ONE of the following options and return the selected option's description as the field value:
- "1: Completely indoor"
- "2: Predominantly indoor"
- "3: Equal indoor/outdoor mix"
- "4: Predominantly outdoor"
- "5: Completely outdoor"
- "X: Not enough information"

For guidance: You must choose one of the above options. A predominantly outdoor space may include gardens or patios, while one without a covering lacks weather protection (e.g., an open field)."""
    )
    privacy: Literal[
        "1: Privacy and exclusivity is a major feature of the venue",
        "2: Moderate privacy with possible nearby non-wedding guests",
        "3: Shared or public space",
        "X: Not enough information",
    ] = Field(
        description="""Assess the privacy level. You MUST CHOOSE ONE of the following options and return the selected option's description as the field value:
- "1: Privacy and exclusivity is a major feature of the venue"
- "2: Moderate privacy with possible nearby non-wedding guests"
- "3: Shared or public space"
- "X: Not enough information"."""
    )
    accommodations: Literal[
        "1: On-site lodging accommodations or extremely close (less than 5 mins walking distance) is possible",
        "2: No On-site lodging, third-party 5-10 minutes away.",
        "3: No on-site lodging, third-party 10+ minutes away.",
        "X: Not enough information",
    ] = Field(
        description="""Determine the lodging accommodations offered by the venue. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:
- "1: On-site lodging accommodations or extremely close (less than 5 mins walking distance) is possible"
- "2: No On-site lodging, third-party 5-10 minutes away."
- "3: No on-site lodging, third-party 10+ minutes away."
- "X: Not enough information"."""
    )
    environmental: Literal[
        "This venue focuses on minimal environmental impact and sustainability in their offering",
        "This venue does not emphasize environment or sustainability",
    ] = Field(
        description="""Assess the venue's emphasis on environmental sustainability. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:
- This venue focuses on minimal environmental impact and sustainability in their offering
- This venue does not emphasize environment or sustainability.

For guidance: A focus on sustainability might include eco-friendly practices (e.g., local sourcing or renewable energy), while lack of emphasis implies no mention of such efforts."""
    )
    general_vibe: Literal[
        "Rustic and simple",
        "Peaceful and serene",
        "Grandiose and elegant",
        "Adventurous or quirky",
        "Warm and cozy",
        "Other",
    ] = Field(
        description="""Determine the general vibe or atmosphere of the venue. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:
- Rustic and simple
- Peaceful and serene
- Grandiose and elegant
- Adventurous or quirky
- Warm and cozy
- Other. For guidance: Rustic and simple might include barns or farms, peaceful and serene could be gardens, grandiose and elegant might be mansions, adventurous or quirky could involve unique spaces, and warm and cozy might be cozy interiors."""
    )


class WeddingVenueOther(BaseModel):
    outside_wedding_coordinator: Literal["True", "False", "unknown"] = Field(
        description="This venue lets me bring in my own wedding coordinator"
    )
    outside_photographer: Literal["True", "False", "unknown"] = Field(
        description="This venue lets me bring in my own photographer"
    )
    package_approach: Literal[
        "1: This venue offers fixed packages, with a few extras or options",
        "2: This venue offers a moderate or flexible approach",
        "3: This venue provides a high degree of flexibility",
        "X: Not enough information",
    ] = Field(
        description="""Determine the wedding package approach of the venue. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:
- "1: This venue offers fixed packages, with a few extras or options"
- "2: This venue offers a moderate or flexible approach"
- "3: This venue provides a high degree of flexibility"
- "X: Not enough information"

For guidance: Fixed packages include in-house services (e.g., pre-set menus); moderate offers a mix; high flexibility requires client planning."""
    )
    reception_or_ceremony: Literal[
        "1: Only space for reception",
        "2: Only space for the ceremony",
        "3: Space for both reception and the ceremony",
        "X: Not enough information",
    ] = Field(
        description="""Determine an option for spaces provided by the venue. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:
- "1: Only space for reception"
- "2: Only space for the ceremony"
- "3: Space for both reception and the ceremony"
- "X: Not enough information"."""
    )
    what_time_does_the_party_need_to_stop: Literal[
        "1: 10PM",
        "2: 12AM",
        "3: After 12AM",
        "X: Not enough information",
    ] = Field(
        description="""Determine the latest time the event must conclude. You MUST CHOOSE ONE of the following options that best matches the document's content:
- "1: 10PM"
- "2: 12AM"
- "3: After 12AM"
- "X: Not enough information"."""
    )
    top_choices: str = Field(
        description="Give me 1-2 reasons why you think a client is most likely to choose this venue (e.g., what are the biggest key selling points or benefits)."
    )
    guest_capacity: Literal["1", "50", "100", "150", "200", "300"] = Field(
        description="""Determine the estimated guest capacity. You MUST CHOOSE ONE of the following approximate maximums that best matches the document's content, representing the upper bound of each range:
- 1 (for 1-50)
- 50 (for 50-100)
- 100 (for 100-150)
- 150 (for 150-200)
- 200 (for 200-300)
- 300 (for 300+)
Guidance: Infer from max guests or room size (e.g., 'up to 150 guests' = 150)."""
    )


def generate_field_instructions(model_class: type[BaseModel]) -> str:
    """Generate field-specific instructions from a Pydantic model's docstrings."""
    instructions = []
    for field_name, field_info in model_class.model_fields.items():
        docstring = (
            field_info.description or field_info.__doc__
        ) or "No description provided."
        instructions.append(f"- {field_name}: {docstring}")
    return "\n".join(instructions)


def create_system_prompt(model_class: type[BaseModel]) -> str:
    field_instructions = generate_field_instructions(model_class)
    tier_hint = model_class.__doc__

    return f"""
        You are an expert in wedding planning. You are extracting structured
        information about wedding venues.

        First, carefully analyze all relevant information in the text. Consider
        both explicit statements and reasonable inferences.

        Important instructions: 
        1. For each field, follow the specific guidelines below about how to handle 
           ambiguous or missing information.
        2. For boolean fields, return true/false values rather than "Yes"/"No" strings. 
        3. For string fields, provide detailed information or null if not available. 
        4. Begin by developing a comprehensive reasoning that considers all evidence 
           before determining individual field values.

        Field-specific instructions:
        {tier_hint}
        {field_instructions}
        """


class WeddingFoodInfo(BaseModel):
    outside_food_allowed: bool = Field(
        description="""Can external catering or food vendors be used at this venue?If the text explicitly mentions allowing outside catering or food vendors, answer True. Do not consider desserts or cakes as food, as these are different categories. If not mentioned, default to False."""
    )
    outside_alcohol_allowed: bool = Field(
        description="""Can external alcohol be brought into this venue?If the text mentions the venue has a liquor license or provides alcohol service, answer False. If the text explicitly mentions allowing outside alcohol or BYOB policy, answer True. If not mentioned, default to False."""
    )
    outside_dessert_allowed: bool = Field(
        description="""Can external desserts or cakes be brought into this venue?If the text explicitly mentions allowing outside desserts or cakes, answer True. If not mentioned, default to True."""
    )
    kosher_food: bool = Field(
        description="""Does the venue offer certified kosher menu options, either in-house or through external vendors?Answer True ONLY if kosher options are explicitly mentioned or if the venue explicitly states they accommodate religious dietary restrictions. If not mentioned, default to False."""
    )
    halal_food: bool = Field(
        description="""Does the venue offer certified halal menu options, either in-house or through external vendors? Return True if offered, False if not offered. Answer True ONLY if halal options are explicitly mentioned. If not mentioned, default to False."""
    )
    east_asian_food: bool = Field(
        description="""Does the venue offer East Asian food options (Chinese, Japanese, Korean, etc.), either in-house or through external vendors? Answer True if East Asian cuisine is explicitly mentioned or if the venue offers international cuisine. If not mentioned, default to False."""
    )
    indian_food: bool = Field(
        description="""Does the venue offer Indian food options, either in-house or through external vendors? Answer True if Indian cuisine is explicitly mentioned or if the venue offers diverse international cuisine that likely includes Indian options. If not mentioned, default to False."""
    )
    gluten_free_food: bool = Field(
        description="""Does the venue offer gluten-free food options? Return True if offered, False if not offered. Answer True if gluten-free options are explicitly mentioned. If the venue mentions accommodating dietary restrictions/allergies/food preferences, return True."""
    )
    other_ethnic_food_style: str = Field(
        description="""Does the venue offer other ethnic food styles beyond those already mentioned? If so, list the available styles as a comma-separated string. If no other ethnic food styles are mentioned, return 'unknown'."""
    )
    late_night_food: bool = Field(
        description="""Does the venue provide late-night food options, such as pizza or snacks after dinner and dessert service? If not mentioned, default to False."""
    )


class WeddingVenuePricingSummary(BaseModel):
    # options: list[WeddingPriceInfo] = Field(
    #     description="This is a list of all the pricing options for this wedding venue."
    # )
    price: int = Field(
        description="""Analyze this wedding venue document and calculate the PER PERSON cost in USD for a 100-guest wedding reception.

Important instructions:
1. Return ONLY a single number representing the per-person cost in USD (e.g., 250)
2. Do NOT return the total venue cost - I need the PER PERSON amount
3. If you see a total price (e.g., $20,000 for 80 guests), divide by the number of guests to get the per-person rate ($20,000 ÷ 80 = $250 per person)
4. Then adjust this per-person rate for a 100-person event, accounting for any tiered pricing

Your calculation must include:
- Food (dinner, appetizer, dessert)
- Beverage/alcohol package
- Venue rental fees (divided by 100 guests)
- All taxes, service charges, and gratuities

Exclude:
- Ceremony costs (focus only on reception)
- Photography
- Late night food
- Any optional add-ons

If multiple packages exist, use the middle-tier or "standard" option.
If specific costs aren't provided, estimate based on the venue's location and quality level.

Think through your calculation step by step:
1. Identify the base per-person food & beverage cost
2. Add any flat venue fees (calculate the per-person amount)
3. Add per-person share of taxes and service charges
4. Sum these components for the final per-person total

Remember: Your answer must be ONLY a single number representing the per-person cost in USD."""
    )
    base_prices: str = Field(
        description="""The base cost of the venue, including menu items,
                    beverages and any variations based on day of the week or
                    package. Break down ALL venue costs on a per-person basis.
                    For example, if the venue has a $20,000 base price for 80
                    guests, the base price per person is $250. If there is not
                    enough information, take the base assumption of $100 per
                    person for food and $50 per person for beverage."""
    )
    taxes_and_fees: str = Field(
        description="The breakdown of taxes, gratuity, and any additional fees, including their individual amounts and the total. Convert ALL taxes, service charges, and fees to per-person amounts. For example, if the venue has a $2,185 tax for 80 guests, the tax per person is $27.31."
    )
    pricing_transparency: Literal[
        "1: This venue discloses a small portion of the total wedding costs",
        "2: This venue discloses a moderate portion of the total wedding costs",
        "3: This venue discloses a high degree of the total costs",
        "X: Not enough information",
    ] = Field(
        description="""Assess how much of the total wedding cost is disclosed in the provided materials. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:

- This venue discloses a small portion of the total wedding costs
- This venue discloses a moderate portion of the total wedding costs
- This venue discloses a high degree of the total wedding costs
- Not enough information

Guidance when selecting the option: A 'small portion' of disclosure means significant costs (e.g., food, bar/alcohol) are unclear or require contacting external vendors. A 'moderate portion' means some unknowns exist, but you can get a general cost idea without much extra work. A 'high degree' means most costs are disclosed with few surprises, little additional work needed to understand the total cost."""
    )
    flexibility: Literal[
        "0: Completely fixed packages, no flexibility",
        "1: Fixed packages with a few extras or options",
        "2: Moderate or flexible approach",
        "3: Highly customizable with some structure",
        "4: Completely custom/DIY",
    ] = Field(
        description="How much freedom does the customer have to customize the wedding/ceremony package?"
    )
    deposit_and_payment_plans: Literal[
        "The venue works with me on deposit terms and payment plans",
        "The venue does not have flexibility on deposit terms and payment plans",
        "Not enough information",
    ] = Field(
        description="""Determine if the venue offers flexibility on deposit terms and payment plans. You MUST CHOOSE ONE of the following options that best matches the document's content and return the selected option's description as the field value:

- The venue works with me on deposit terms and payment plans
- The venue does not have flexibility on deposit terms and payment plans
- Not enough information.

Follow these guidance when selecting the option: Flexibility means the venue allows negotiation on deposit amounts, payment schedules, or offers installment plans. Lack of flexibility is indicated by strict terms or no mention of flexible options."""
    )
