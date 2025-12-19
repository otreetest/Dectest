import random

from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'pre'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ATTENTION_CHECK_NUM = random.randint(0, 100)
    ATTENTION_CHECK_NUM2 = random.randint(0, 100)
    ATTENTION_CHECK_NUM3 = random.randint(0, 100)


def creating_session(subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            player.attention_check_num = random.randint(0, 100)
            player.attention_check_num2 = random.randint(0, 100)
            player.attention_check_num3 = random.randint(0, 100)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField()

    attention_check_num = models.IntegerField()
    attention_check_num2 = models.IntegerField()
    attention_check_num3 = models.IntegerField()

    attention_check = models.IntegerField(
        label='What number were you asked to remember?'
    )

    attention_check2 = models.IntegerField(
        label='What number were you asked to remember?'
    )

    attention_check3 = models.IntegerField(
        label='What number were you asked to remember?'
    )


# PAGES
class Preview(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        
        # 从 URL 参数获取 Prolific ID 并保存
        if participant.label:
            participant.prolific_id = participant.label
            print(f"DEBUG: Prolific ID saved: {participant.prolific_id}")
        else:
            print("DEBUG: No Participant Label found in URL.")

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if not player.consent:
            return 'end'


class AttentionCheck1(Page):
    pass


class AttentionCheck1_2(Page):
    form_model = 'player'
    form_fields = ['attention_check']


class AttentionCheck1_3(Page):

    @staticmethod
    def is_displayed(player):
        return player.attention_check != player.attention_check_num


class AttentionCheck2(Page):

    @staticmethod
    def is_displayed(player):
        return player.attention_check != player.attention_check_num


class AttentionCheck2_2(Page):
    @staticmethod
    def is_displayed(player):
        return player.attention_check != player.attention_check_num

    form_model = 'player'
    form_fields = ['attention_check2']


class AttentionCheck2_3(Page):
    @staticmethod
    def is_displayed(player):
        if player.field_maybe_none('attention_check2') is None:
            return False  # Skip page if attention_check2 is None
        return player.attention_check2 != player.attention_check_num2


class AttentionCheck3(Page):
    @staticmethod
    def is_displayed(player):
        return (player.attention_check != player.attention_check_num
                and player.attention_check2 is not None
                and player.attention_check2 != player.attention_check_num2)


class AttentionCheck3_2(Page):
    @staticmethod
    def is_displayed(player):
        return player.field_maybe_none('attention_check2') not in [None, player.attention_check_num2]

    form_model = 'player'
    form_fields = ['attention_check3']


class AttentionCheck3_3(Page):
    @staticmethod
    def is_displayed(player):
        return player.field_maybe_none('attention_check3') not in [None, player.attention_check_num3]

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.attention_check3 != player.attention_check_num3:
            return 'end2'


page_sequence = [
    Preview,
    AttentionCheck1,
    AttentionCheck1_2,
    AttentionCheck1_3,
    AttentionCheck2,
    AttentionCheck2_2,
    AttentionCheck2_3,
    AttentionCheck3,
    AttentionCheck3_2,
    AttentionCheck3_3,
]
