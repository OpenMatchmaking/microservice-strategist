from app.algorithms.base import BaseAlgorithm
from app.algorithms.structures import TeamInfo


class SimpleAverage(BaseAlgorithm):
    """
    Simple matchmaking algorithm, based on comparison by average skill rating
    between the players / teams. If the player can't grouped up with in
    existing environment, then returns everything as is, without any changes.
    """
    def get_average_team_rating(self, team):
        if team:
            return sum([player["detail"]["rating"] for player in team]) // len(team)
        return 0

    def get_players_count(self, team):
        return len(team)

    def get_teams_info(self, teams):
        def team_info(team_name):
            return TeamInfo(
                name=team_name,
                rating=self.get_average_team_rating(teams[team_name]),
                players_count=self.get_players_count(teams[team_name])
            )
        return list(map(team_info, teams))

    def find_suitable_team(self, teams_info):
        teams_info.sort(key=lambda team: team.players_count)
        suitable_team = teams_info[0] if teams_info else None
        return suitable_team

    def find_team_by_name(self, teams_info, value):
        for index, team in enumerate(teams_info):
            if team.name == value:
                return index

    def calculate_new_team_rating(self, player, suitable_team):
        player_rating = player["detail"]["rating"]
        if suitable_team.players_count == 0:
            team_rating = player_rating
        else:
            team_rating = (suitable_team.rating + player_rating) // 2
        return team_rating

    def update_teams_info(self, player, suitable_team, teams_info):
        updated_team_info = TeamInfo(
            name=suitable_team.name,
            rating=self.calculate_new_team_rating(player, suitable_team),
            players_count=suitable_team.players_count + 1
        )
        replace_item_index = self.find_team_by_name(teams_info, suitable_team.name)
        teams_info[replace_item_index] = updated_team_info

    def is_fair_seeding(self, player, suitable_team, teams_info, max_difference):
        self.update_teams_info(player, suitable_team, teams_info)

        results = []
        filled_teams = [team for team in teams_info if team.players_count > 0]
        filled_teams_count = len(filled_teams)

        if filled_teams_count > 1:
            for team in teams_info:
                sum_difference = sum([
                    abs(team.rating - enemy_team.rating)
                    for enemy_team in teams_info
                    if team.name != enemy_team.name
                ])
                average_difference = sum_difference // filled_teams_count
                results.append(average_difference)

        return all([difference <= max_difference for difference in results])

    def seed_player(self, player, teams, max_difference=25, **kwargs):
        added, updated_teams = False, teams

        teams_info = self.get_teams_info(teams)
        suitable_team = self.find_suitable_team(teams_info)

        if suitable_team and self.is_fair_seeding(player, suitable_team, teams_info, max_difference):
            added = True
            updated_teams[suitable_team.name].append(player)

        return added, updated_teams
