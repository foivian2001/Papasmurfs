from decimal import Decimal, ROUND_CEILING

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogue.models import (
    BoostPackage,
    Game,
    Rank,
    ServiceCategory,
)


# ============================================================
# CATEGORY CONFIGURATION
# ============================================================

CATEGORY_CONFIG = [
    {
        "game": "League of Legends",
        "category": "Solo/Duo Rank Boosting",
        "base_rate": Decimal("7.50"),
        "pace": Decimal("3.30"),
        "short_name": "Solo/Duo",
    },
    {
        "game": "Counter-Strike 2",
        "category": "Competitive Rank Boost",
        "base_rate": Decimal("8.25"),
        "pace": Decimal("3.10"),
        "short_name": "Competitive",
    },
    {
        "game": "Fortnite",
        "category": "Build Mode Rank Boosting",
        "base_rate": Decimal("7.25"),
        "pace": Decimal("3.30"),
        "short_name": "Build Mode",
    },
    {
        "game": "Fortnite",
        "category": "Zero Build Rank Boosting",
        "base_rate": Decimal("6.75"),
        "pace": Decimal("3.40"),
        "short_name": "Zero Build",
    },
    {
        "game": "GTA Online",
        "category": "RP / Level Boosting",
        "base_rate": None,
        "pace": None,
        "short_name": "RP / Level",
    },
]


# ============================================================
# IMPORTANT TARGET RANKS
# ============================================================

MILESTONE_TARGETS = {
    "League of Legends": [
        "Bronze IV",
        "Silver IV",
        "Gold IV",
        "Platinum IV",
        "Emerald IV",
        "Diamond IV",
        "Master",
        "Grandmaster",
    ],

    "Counter-Strike 2": [
        "Gold Nova I",
        "Master Guardian I",
        "Legendary Eagle",
        "Global Elite",
    ],

    "Fortnite": [
        "Silver I",
        "Gold I",
        "Platinum I",
        "Diamond I",
        "Elite",
        "Champion",
        "Unreal",
    ],
}


# ============================================================
# SELECTED LONG-DISTANCE PACKAGES
# ============================================================

LONG_JUMPS = {
    "League of Legends": [
        ("Iron IV", "Gold IV"),
        ("Bronze IV", "Platinum IV"),
        ("Silver IV", "Emerald IV"),
        ("Gold IV", "Diamond IV"),
        ("Platinum IV", "Master"),
        ("Emerald IV", "Grandmaster"),
    ],

    "Counter-Strike 2": [
        ("Silver I", "Gold Nova I"),
        ("Gold Nova I", "Master Guardian I"),
        ("Master Guardian I", "Legendary Eagle"),
        ("Legendary Eagle", "Global Elite"),
    ],

    "Fortnite": [
        ("Bronze I", "Gold I"),
        ("Silver I", "Platinum I"),
        ("Gold I", "Diamond I"),
        ("Platinum I", "Elite"),
        ("Diamond I", "Unreal"),
    ],
}


# ============================================================
# EXACTLY FIVE INACTIVE PACKAGES
# ============================================================

INACTIVE_PACKAGES = {
    (
        "League of Legends",
        "Solo/Duo Rank Boosting",
        "Iron IV",
        "Gold IV",
    ),

    (
        "Counter-Strike 2",
        "Competitive Rank Boost",
        "Silver I",
        "Gold Nova I",
    ),

    (
        "Fortnite",
        "Build Mode Rank Boosting",
        "Bronze I",
        "Gold I",
    ),

    (
        "Fortnite",
        "Zero Build Rank Boosting",
        "Silver I",
        "Platinum I",
    ),

    (
        "GTA Online",
        "RP / Level Boosting",
        "Level 1",
        "Level 75",
    ),
}


# ============================================================
# FEATURED PACKAGES
# ============================================================

FEATURED_PACKAGES = {
    (
        "League of Legends",
        "Solo/Duo Rank Boosting",
        "Silver IV",
        "Gold IV",
    ),

    (
        "League of Legends",
        "Solo/Duo Rank Boosting",
        "Gold IV",
        "Platinum IV",
    ),

    (
        "League of Legends",
        "Solo/Duo Rank Boosting",
        "Platinum IV",
        "Diamond IV",
    ),

    (
        "League of Legends",
        "Solo/Duo Rank Boosting",
        "Diamond IV",
        "Master",
    ),

    (
        "Counter-Strike 2",
        "Competitive Rank Boost",
        "Gold Nova I",
        "Master Guardian I",
    ),

    (
        "Counter-Strike 2",
        "Competitive Rank Boost",
        "Master Guardian I",
        "Legendary Eagle",
    ),

    (
        "Fortnite",
        "Build Mode Rank Boosting",
        "Gold I",
        "Diamond I",
    ),

    (
        "Fortnite",
        "Zero Build Rank Boosting",
        "Platinum I",
        "Elite",
    ),

    (
        "GTA Online",
        "RP / Level Boosting",
        "Level 1",
        "Level 100",
    ),

    (
        "GTA Online",
        "RP / Level Boosting",
        "Level 100",
        "Level 200",
    ),
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def price_ending_99(value):
    """
    Convert a calculated price to a clean commercial price
    ending in .99.
    """

    rounded_up = value.to_integral_value(
        rounding=ROUND_CEILING
    )

    return rounded_up - Decimal("0.01")


def calculate_ranked_effort(
    ranks,
    current_index,
    target_index,
):
    """
    Calculate workload for a ranked-game package.

    Higher divisions cost more effort per rank because progression
    becomes more difficult at the top of the ladder.
    """

    maximum_order = Decimal(
        str(ranks[-1].rank_order)
    )

    effort = Decimal("0.00")

    for index in range(
        current_index + 1,
        target_index + 1,
    ):

        rank_order = Decimal(
            str(ranks[index].rank_order)
        )

        difficulty_bonus = (
            Decimal("1.00")
            + (
                (rank_order - Decimal("1"))
                / maximum_order
                * Decimal("1.10")
            )
        )

        effort += difficulty_bonus

    return effort


def calculate_ranked_price(
    ranks,
    current_index,
    target_index,
    base_rate,
):
    """
    Rank difference and high-rank difficulty both affect price.
    """

    effort = calculate_ranked_effort(
        ranks,
        current_index,
        target_index,
    )

    base_fee = Decimal("5.00")

    raw_price = (
        base_fee
        + effort * base_rate
    )

    return price_ending_99(raw_price)


def calculate_ranked_days(
    ranks,
    current_index,
    target_index,
    pace,
):
    """
    Convert workload into estimated completion time.
    """

    effort = calculate_ranked_effort(
        ranks,
        current_index,
        target_index,
    )

    days = (
        effort / pace
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    days = max(1, int(days))

    return min(days, 14)


def gta_level(rank_name):
    """
    Convert 'Level 100' into integer 100.
    """

    return int(
        rank_name.replace("Level ", "")
    )


def calculate_gta_price(
    current_rank,
    target_rank,
):
    """
    GTA pricing is based on the real level difference.

    Higher account levels cost slightly more per level.
    """

    current = gta_level(current_rank.name)
    target = gta_level(target_rank.name)

    raw_price = Decimal("10.00")

    for level in range(
        current + 1,
        target + 1,
    ):

        if level <= 50:
            rate = Decimal("0.35")

        elif level <= 100:
            rate = Decimal("0.45")

        elif level <= 150:
            rate = Decimal("0.55")

        else:
            rate = Decimal("0.65")

        raw_price += rate

    return price_ending_99(raw_price)


def calculate_gta_days(
    current_rank,
    target_rank,
):
    """
    GTA completion time is based on the number
    of levels that need to be gained.
    """

    current = gta_level(current_rank.name)
    target = gta_level(target_rank.name)

    difference = target - current

    days = (
        Decimal(str(difference))
        / Decimal("30")
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    return max(1, min(int(days), 10))


def build_ranked_pairs(
    game_name,
    ranks,
):
    """
    Generate useful package combinations.

    Includes:
    - +1 rank
    - +2 ranks
    - +3 ranks
    - medium jumps to important milestones
    - selected long-distance packages
    """

    pairs = set()

    rank_indexes = {
        rank.name: index
        for index, rank in enumerate(ranks)
    }

    total = len(ranks)

    # Every short-distance combination.
    for current_index in range(total):

        for difference in (1, 2, 3):

            target_index = (
                current_index + difference
            )

            if target_index < total:

                pairs.add(
                    (
                        ranks[current_index].name,
                        ranks[target_index].name,
                    )
                )

    # Medium-distance jumps toward important milestones.
    for current_index, current_rank in enumerate(ranks):

        for target_name in MILESTONE_TARGETS[
            game_name
        ]:

            target_index = rank_indexes[
                target_name
            ]

            difference = (
                target_index - current_index
            )

            if 4 <= difference <= 8:

                pairs.add(
                    (
                        current_rank.name,
                        target_name,
                    )
                )

    # Selected larger jumps.
    for pair in LONG_JUMPS[game_name]:
        pairs.add(pair)

    return sorted(
        pairs,
        key=lambda pair: (
            rank_indexes[pair[0]],
            rank_indexes[pair[1]],
        ),
    )


def build_gta_pairs(ranks):
    """
    GTA has only seven progression milestones,
    so every valid milestone combination is useful.
    """

    pairs = []

    for current_index in range(len(ranks)):

        for target_index in range(
            current_index + 1,
            len(ranks),
        ):

            pairs.append(
                (
                    ranks[current_index].name,
                    ranks[target_index].name,
                )
            )

    return pairs


def package_name(
    game_name,
    category_name,
    current_name,
    target_name,
):
    """
    Generate readable catalogue package names.
    """

    if game_name == "League of Legends":

        return (
            f"{current_name} to {target_name} "
            f"Solo/Duo Boost"
        )

    if game_name == "Counter-Strike 2":

        return (
            f"{current_name} to {target_name} "
            f"Competitive Boost"
        )

    if game_name == "Fortnite":

        if category_name == (
            "Zero Build Rank Boosting"
        ):

            mode = "Zero Build"

        else:
            mode = "Build Mode"

        return (
            f"{current_name} to {target_name} "
            f"{mode} Boost"
        )

    if game_name == "GTA Online":

        return (
            f"{current_name} to {target_name} "
            f"RP Boost"
        )

    return (
        f"{current_name} to {target_name} Boost"
    )


def package_description(
    game_name,
    category_name,
    current_name,
    target_name,
    days,
):
    """
    Generate useful package descriptions.
    """

    day_word = (
        "day"
        if days == 1
        else "days"
    )

    if game_name == "League of Legends":

        return (
            f"Progress your League of Legends "
            f"Ranked Solo/Duo account from "
            f"{current_name} to {target_name}. "
            f"Estimated completion time: "
            f"{days} {day_word}."
        )

    if game_name == "Counter-Strike 2":

        return (
            f"Progress your Counter-Strike 2 "
            f"competitive rank from "
            f"{current_name} to {target_name}. "
            f"Estimated completion time: "
            f"{days} {day_word}."
        )

    if game_name == "Fortnite":

        if category_name == (
            "Zero Build Rank Boosting"
        ):

            mode = "Zero Build"

        else:
            mode = "Build Mode"

        return (
            f"Progress from {current_name} "
            f"to {target_name} in Fortnite "
            f"{mode} Ranked. "
            f"Estimated completion time: "
            f"{days} {day_word}."
        )

    if game_name == "GTA Online":

        return (
            f"Increase your GTA Online account "
            f"from {current_name} to {target_name} "
            f"through RP and level progression. "
            f"Estimated completion time: "
            f"{days} {day_word}."
        )

    return (
        f"Progress from {current_name} "
        f"to {target_name}. "
        f"Estimated completion time: "
        f"{days} {day_word}."
    )


def game_image_value(game):
    """
    Reuse the Game's Cloudinary image for packages.

    This gives every generated package a working catalogue
    image without uploading hundreds of duplicate files.
    """

    if not game.image:
        return ""

    if hasattr(game.image, "public_id"):
        return game.image.public_id

    return str(game.image)


# ============================================================
# DJANGO COMMAND
# ============================================================

class Command(BaseCommand):

    help = (
        "Create a varied Papasmurfs boost-package "
        "catalogue with calculated prices and "
        "completion times."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Validate the production data and show "
                "how many packages would be generated "
                "without saving anything."
            ),
        )

    @transaction.atomic
    def handle(
        self,
        *args,
        **options,
    ):

        dry_run = options["dry_run"]

        self.stdout.write("")
        self.stdout.write(
            "Papasmurfs package seeder"
        )
        self.stdout.write(
            "========================="
        )

        # ----------------------------------------------------
        # PRE-FLIGHT CHECK
        # ----------------------------------------------------

        missing_items = []

        configurations = []

        for config in CATEGORY_CONFIG:

            game_name = config["game"]
            category_name = config["category"]

            try:

                game = Game.objects.get(
                    name=game_name
                )

            except Game.DoesNotExist:

                missing_items.append(
                    f"Missing game: {game_name}"
                )

                continue

            try:

                category = (
                    ServiceCategory.objects.get(
                        game=game,
                        name=category_name,
                    )
                )

            except ServiceCategory.DoesNotExist:

                missing_items.append(
                    "Missing category: "
                    f"{game_name} / {category_name}"
                )

                continue

            ranks = list(
                Rank.objects.filter(
                    game=game
                ).order_by("rank_order")
            )

            if len(ranks) < 2:

                missing_items.append(
                    f"Not enough ranks for {game_name}"
                )

                continue

            configurations.append(
                (
                    config,
                    game,
                    category,
                    ranks,
                )
            )

        if missing_items:

            message = (
                "\n".join(missing_items)
            )

            raise CommandError(
                "\nPackage seeding stopped.\n"
                "Fix these items first:\n"
                f"{message}"
            )

        # ----------------------------------------------------
        # BUILD PACKAGE SPECIFICATIONS
        # ----------------------------------------------------

        specifications = []

        for (
            config,
            game,
            category,
            ranks,
        ) in configurations:

            rank_lookup = {
                rank.name: rank
                for rank in ranks
            }

            rank_indexes = {
                rank.name: index
                for index, rank in enumerate(ranks)
            }

            if game.name == "GTA Online":

                pairs = build_gta_pairs(ranks)

            else:

                pairs = build_ranked_pairs(
                    game.name,
                    ranks,
                )

            for (
                current_name,
                target_name,
            ) in pairs:

                current_rank = rank_lookup[
                    current_name
                ]

                target_rank = rank_lookup[
                    target_name
                ]

                if game.name == "GTA Online":

                    price = calculate_gta_price(
                        current_rank,
                        target_rank,
                    )

                    days = calculate_gta_days(
                        current_rank,
                        target_rank,
                    )

                else:

                    current_index = rank_indexes[
                        current_name
                    ]

                    target_index = rank_indexes[
                        target_name
                    ]

                    price = calculate_ranked_price(
                        ranks,
                        current_index,
                        target_index,
                        config["base_rate"],
                    )

                    days = calculate_ranked_days(
                        ranks,
                        current_index,
                        target_index,
                        config["pace"],
                    )

                identity = (
                    game.name,
                    category.name,
                    current_name,
                    target_name,
                )

                is_active = (
                    identity
                    not in INACTIVE_PACKAGES
                )

                is_featured = (
                    identity
                    in FEATURED_PACKAGES
                    and is_active
                )

                specifications.append(
                    {
                        "game": game,
                        "category": category,
                        "current_rank": current_rank,
                        "target_rank": target_rank,
                        "name": package_name(
                            game.name,
                            category.name,
                            current_name,
                            target_name,
                        ),
                        "description": (
                            package_description(
                                game.name,
                                category.name,
                                current_name,
                                target_name,
                                days,
                            )
                        ),
                        "price": price,
                        "estimated_days": days,
                        "is_active": is_active,
                        "is_featured": is_featured,
                    }
                )

        # ----------------------------------------------------
        # DRY RUN
        # ----------------------------------------------------

        active_count = sum(
            1
            for specification in specifications
            if specification["is_active"]
        )

        inactive_count = (
            len(specifications)
            - active_count
        )

        featured_count = sum(
            1
            for specification in specifications
            if specification["is_featured"]
        )

        prices = [
            specification["price"]
            for specification in specifications
        ]

        times = [
            specification["estimated_days"]
            for specification in specifications
        ]

        self.stdout.write("")
        self.stdout.write(
            f"Packages prepared: "
            f"{len(specifications)}"
        )

        self.stdout.write(
            f"Active: {active_count}"
        )

        self.stdout.write(
            f"Inactive: {inactive_count}"
        )

        self.stdout.write(
            f"Featured: {featured_count}"
        )

        self.stdout.write(
            f"Price range: "
            f"€{min(prices)} - €{max(prices)}"
        )

        self.stdout.write(
            f"Completion range: "
            f"{min(times)} - {max(times)} days"
        )

        if dry_run:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN: no packages were saved."
                )
            )

            transaction.set_rollback(True)

            return

        # ----------------------------------------------------
        # SAVE PACKAGES
        # ----------------------------------------------------

        created_count = 0
        updated_count = 0

        for specification in specifications:

            game = specification["game"]

            existing_package = (
                BoostPackage.objects.filter(
                    category=specification[
                        "category"
                    ],
                    current_rank=specification[
                        "current_rank"
                    ],
                    target_rank=specification[
                        "target_rank"
                    ],
                )
                .order_by("id")
                .first()
            )

            if existing_package:

                package = existing_package

                package.name = specification[
                    "name"
                ]

                package.description = (
                    specification[
                        "description"
                    ]
                )

                package.price = specification[
                    "price"
                ]

                package.estimated_days = (
                    specification[
                        "estimated_days"
                    ]
                )

                package.is_active = (
                    specification[
                        "is_active"
                    ]
                )

                package.is_featured = (
                    specification[
                        "is_featured"
                    ]
                )

                # Preserve a custom package image if one
                # has already been uploaded.
                if not package.image:

                    package.image = (
                        game_image_value(game)
                    )

                package.full_clean()
                package.save()

                updated_count += 1

            else:

                package = BoostPackage(
                    category=specification[
                        "category"
                    ],
                    current_rank=specification[
                        "current_rank"
                    ],
                    target_rank=specification[
                        "target_rank"
                    ],
                    name=specification[
                        "name"
                    ],
                    description=specification[
                        "description"
                    ],
                    price=specification[
                        "price"
                    ],
                    estimated_days=specification[
                        "estimated_days"
                    ],
                    image=game_image_value(game),
                    is_active=specification[
                        "is_active"
                    ],
                    is_featured=specification[
                        "is_featured"
                    ],
                )

                package.full_clean()
                package.save()

                created_count += 1

        # ----------------------------------------------------
        # FINISHED
        # ----------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            "========================="
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Package catalogue generated "
                "successfully."
            )
        )

        self.stdout.write("")
