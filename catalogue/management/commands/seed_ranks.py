from django.core.management.base import BaseCommand
from django.db import transaction

from catalogue.models import Game, Rank


RANK_DATA = {
    "League of Legends": [
        ("Iron IV", 1),
        ("Iron III", 2),
        ("Iron II", 3),
        ("Iron I", 4),
        ("Bronze IV", 5),
        ("Bronze III", 6),
        ("Bronze II", 7),
        ("Bronze I", 8),
        ("Silver IV", 9),
        ("Silver III", 10),
        ("Silver II", 11),
        ("Silver I", 12),
        ("Gold IV", 13),
        ("Gold III", 14),
        ("Gold II", 15),
        ("Gold I", 16),
        ("Platinum IV", 17),
        ("Platinum III", 18),
        ("Platinum II", 19),
        ("Platinum I", 20),
        ("Emerald IV", 21),
        ("Emerald III", 22),
        ("Emerald II", 23),
        ("Emerald I", 24),
        ("Diamond IV", 25),
        ("Diamond III", 26),
        ("Diamond II", 27),
        ("Diamond I", 28),
        ("Master", 29),
        ("Grandmaster", 30),
    ],

    "Counter-Strike 2": [
        ("Silver I", 1),
        ("Silver II", 2),
        ("Silver III", 3),
        ("Silver IV", 4),
        ("Silver Elite", 5),
        ("Silver Elite Master", 6),
        ("Gold Nova I", 7),
        ("Gold Nova II", 8),
        ("Gold Nova III", 9),
        ("Gold Nova Master", 10),
        ("Master Guardian I", 11),
        ("Master Guardian II", 12),
        ("Master Guardian Elite", 13),
        ("Distinguished Master Guardian", 14),
        ("Legendary Eagle", 15),
        ("Legendary Eagle Master", 16),
        ("Supreme Master First Class", 17),
        ("Global Elite", 18),
    ],

    "Fortnite": [
        ("Bronze I", 1),
        ("Bronze II", 2),
        ("Bronze III", 3),
        ("Silver I", 4),
        ("Silver II", 5),
        ("Silver III", 6),
        ("Gold I", 7),
        ("Gold II", 8),
        ("Gold III", 9),
        ("Platinum I", 10),
        ("Platinum II", 11),
        ("Platinum III", 12),
        ("Diamond I", 13),
        ("Diamond II", 14),
        ("Diamond III", 15),
        ("Elite", 16),
        ("Champion", 17),
        ("Unreal", 18),
    ],

    "GTA Online": [
        ("Level 1", 1),
        ("Level 25", 2),
        ("Level 50", 3),
        ("Level 75", 4),
        ("Level 100", 5),
        ("Level 150", 6),
        ("Level 200", 7),
    ],
}


class Command(BaseCommand):
    help = "Create the Papasmurfs rank/progression data for all games."

    @transaction.atomic
    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        self.stdout.write("")
        self.stdout.write("Papasmurfs rank seeder")
        self.stdout.write("----------------------")

        for game_name, ranks in RANK_DATA.items():

            try:
                game = Game.objects.get(name=game_name)
            except Game.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Game not found: {game_name}. "
                        "Create the game first."
                    )
                )
                continue

            self.stdout.write("")
            self.stdout.write(f"{game_name}:")

            for rank_name, rank_order in ranks:

                rank, created = Rank.objects.get_or_create(
                    game=game,
                    name=rank_name,
                    defaults={
                        "rank_order": rank_order,
                    },
                )

                if created:
                    created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  + {rank_name} ({rank_order})"
                        )
                    )

                else:
                    existing_count += 1

                    # Keep the correct order if an existing
                    # rank has an incorrect value.
                    if rank.rank_order != rank_order:
                        rank.rank_order = rank_order
                        rank.save(update_fields=["rank_order"])

                        self.stdout.write(
                            self.style.WARNING(
                                f"  ~ Updated {rank_name} "
                                f"to order {rank_order}"
                            )
                        )
                    else:
                        self.stdout.write(
                            f"  = {rank_name} already exists"
                        )

        self.stdout.write("")
        self.stdout.write("----------------------")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count}"
            )
        )

        self.stdout.write(
            f"Already existing: {existing_count}"
        )

        total_ranks = Rank.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Total ranks in database: {total_ranks}"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Rank seeding completed successfully."
            )
        )