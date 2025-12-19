import random
import csv
import os
from otree.api import *
from datetime import datetime

doc = """
Two-stage experiment with manager-employee matching
"""

current_dir = os.path.dirname(os.path.abspath(__file__))

class C(BaseConstants):
    NAME_IN_URL = 'main' 
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PREFER_CHOICES = ['Left', 'Right']
    CHALLENGE_CHOICES = ['Red Cross', 'NRA']
    SURVEY_M_QUESTIONS = [
        'I see myself as a member of the team.',
        'I am glad to be in this team.',
        'I feel strong ties with the team.',
        'I identify myself with the department.',
    ]
    SURVEY_O_QUESTIONS = [
        'I am proud of the contribution to social causes of my organization.',
        'I feel aligned with the values of my organization.',
        'I identify with my organization.',
        'I feel connected to my organization.',
        'I feel comfortable working in my organization.',
        'I feel motivated working in my organization.',
        'I want to stay in my organization.',
    ]
    
    # Path to the CSV file containing manager data
    MANAGER_DATA_PATH = current_dir + '/input.csv'

    # Big5
    CHOICES = range(1, 6)
    QUESTIONS = [
        '...is reserved',
        '...generally trusting',
        '...tends to be lazy',
        '...is relaxed, handles stress well',
        '...has few artistic interests',
        '...does things efficiently',
        '...is outgoing, sociable',
        '...tends to find fault with others',
        '...does a thorough job',
        '...gets nervous easily',
        '...has an active imagination',
        '...perseveres until the task is finished',
    ]

    COMPARISON_QUESTIONS = [
        'I always pay a lot of attention to how I do things compared with how others do things.',
        'I am not the type of person who compares often with others.',
        'I often compare how I am doing socially (e.g., social skills, popularity) with other people.',
        'I see myself as someone who enjoys winning and hates losing.',
        'I see myself as someone who enjoys competing, regardless of whether I win or lose.',
        'I see myself as a competitive person.',
        'Competition brings the best out of me.',
    ]

    DICTATOR_ENDOWMENT = 10

    # Add demographic questions constants
    AGE_LABEL = "What is your age?"
    
    GENDER_LABEL = "What is your gender?"
    GENDER_CHOICES = ["Male", "Female", "Non-binary","Prefer not to say"]
    
    EDUCATION_LABEL = "Please indicate the highest level of education completed"
    EDUCATION_CHOICES = [
        "Less than High School",
        "High School or equivalent",
        "Vocational/Technical School (2 years)",
        "Some College",
        "College Graduate (4 years)",
        "Master's Degree (MA)",
        "Doctoral Degree (PhD)"
    ]

    INCOME_LABEL = "What is your annual household income?"
    INCOME_CHOICES = [
        "Less than $25,000",
        "$25,000 - $49,999",
        "$50,000 - $74,999",
        "$75,000 - $99,999",
        "$100,000 - $149,999",
        "$150,000 or more",
        "Prefer not to say"
    ]
    
    # Demographics - Employment
    EMPLOYMENT_LABEL = "What is your current employment status?"
    EMPLOYMENT_CHOICES = [
        "Full-time employed",
        "Part-time employed",
        "Self-employed",
        "Unemployed",
        "Student",
        "Retired",
        "Unable to work",
        "Other"
    ]
    
    # Demographics - Occupation/Industry
    OCCUPATION_LABEL = "What industry do you work in (or most recently worked in)?"
    OCCUPATION_CHOICES = [
        "Education",
        "Healthcare",
        "Technology/IT",
        "Finance/Banking",
        "Retail/Sales",
        "Manufacturing",
        "Government/Public Service",
        "Arts/Entertainment",
        "Construction/Trades",
        "Transportation/Logistics",
        "Hospitality/Food Service",
        "Legal/Professional Services",
        "Non-profit/NGO",
        "Other"
    ]


class Subsession(BaseSubsession):
    pass


def creating_session(self:Subsession):
    # Load manager data from CSV using standard library
    if os.path.exists(C.MANAGER_DATA_PATH):
        try:
            # Load the CSV file
            manager_data = []
            header = []
            with open(C.MANAGER_DATA_PATH, 'r', encoding='utf-8-sig') as csvfile:
                csv_reader = csv.reader(csvfile)
                header = next(csv_reader)  # Get header row
                for row in csv_reader:
                    manager_data.append(row)
            # Create a dictionary to map column names to indices
            column_indices = {name: idx for idx, name in enumerate(header)}

            # Store the data in session vars
            self.session.vars['manager_data'] = manager_data
            self.session.vars['manager_data_header'] = header
            self.session.vars['manager_data_columns'] = column_indices
            
            self.session.vars['used_manager_ids'] = []
            
            self.session.vars['session_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            num_players = len(self.get_players())
            num_managers = len(manager_data)
            print(f"\n{'='*50}")
            print(f"SESSION INITIALIZATION")
            print(f"{'='*50}")
            print(f"Session code: {self.session.code}")
            print(f"Session start: {self.session.vars['session_start_time']}")
            print(f"Players in session: {num_players}")
            print(f"Managers available: {num_managers}")
            print(f"CSV columns: {header}")
            
            if num_managers < num_players:
                print(f"\n⚠️  WARNING: Not enough managers!")
                print(f"   Need: {num_players}")
                print(f"   Have: {num_managers}")
                print(f"   Shortage: {num_players - num_managers}")
            else:
                print(f"\n✓ Sufficient managers available")
                print(f"  Surplus: {num_managers - num_players}")
            print(f"{'='*50}\n")
                
        except Exception as e:
            print(f"\n❌ Error loading manager data: {e}")
            import traceback
            traceback.print_exc()
            # Create empty data as fallback
            self.session.vars['manager_data'] = []
            self.session.vars['manager_data_header'] = []
            self.session.vars['manager_data_columns'] = {}
            self.session.vars['used_manager_ids'] = []
    else:
        print(f"\n❌ Manager data file not found: {C.MANAGER_DATA_PATH}")
        print(f"   Current directory: {current_dir}")
        print(f"   Please ensure input.csv exists in the correct location")
        # Create empty data as fallback
        self.session.vars['manager_data'] = []
        self.session.vars['manager_data_header'] = []
        self.session.vars['manager_data_columns'] = {}
        self.session.vars['used_manager_ids'] = []

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    group_prefer = models.StringField()
    group_team = models.StringField()
    group_organization = models.StringField()
    group_manager_id = models.StringField()
    group_manager_prefer = models.StringField()
    
    # Store the matched manager's ID for reference
    matched_manager_id = models.StringField()
    manager_match_order = models.IntegerField(blank=True)
    manager_match_timestamp = models.StringField(blank=True)

    # Store the matched manager's data for reference
    manager_stated_amount = models.StringField()
    manager_correct_amount = models.StringField()
    manager_threshold_integer = models.StringField()

    prefer = models.StringField(
        label="<b>Please select your preferred painting from the options below:</b>",
        choices=C.PREFER_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )
    charity_1 = models.StringField(
        label="<img src='/static/img/RedCross.png' style='width: 160px; max-width: 100%;'>  <img src='/static/img/NRA.png' style='width: 160px; max-width: 100%;'><br><br>Which charity do you identify with?",
        choices=C.CHALLENGE_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )
    charity_2 = models.StringField(
        label="If your organization donates to a charity, which one would you prefer?",
        choices=C.CHALLENGE_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )

    report_rand_int = models.IntegerField()

    report_probability = models.IntegerField(
        label='<b>How likely are you to report your manager?</b>',
        min=0,
        max=100,
    )
    report = models.BooleanField()
    
    choiceE = models.CharField(
        label="<img src='/static/img/PaulKlee.jpg' style='width: 160px; max-width: 100%;'>  <img src='/static/img/VassilyKandinsky.jpg' style='width: 160px; max-width: 100%;'><br><br>1) Please indicate the painting that <b>you selected</b> at the beginning of the game:<br>",
        choices=["Klee", "Kandinsky"],
        widget=widgets.RadioSelectHorizontal,  # Changed from RadioSelect to RadioSelectHorizontal
        blank=False
    )

    choiceM = models.CharField(
        label="2) Please indicate the painting that <b>your manager selected </b>at the beginning of the game:<br>",
        choices=["Klee", "Kandinsky"],
        widget=widgets.RadioSelectHorizontal,  # Changed from RadioSelect to RadioSelectHorizontal
        blank=False
    )

    choiceT = models.CharField(
        label="3) Please indicate the painting that <b>represented your team</b>:<br>",
        choices=["Klee", "Kandinsky"],
        widget=widgets.RadioSelectHorizontal,  # Changed from RadioSelect to RadioSelectHorizontal
        blank=False
    )

    choiceO = models.CharField(
        label="<br><img src='/static/img/RedCross.png' style='width: 160px; max-width: 100%;'>  <img src='/static/img/NRA.png' style='width: 160px; max-width: 100%;'><br><br>4) Please indicate the charity that your <b>organization donated to</b>:<br>",
        choices=["Red Cross", "NRA"],
        widget=widgets.RadioSelectHorizontal,  # Changed from RadioSelect to RadioSelectHorizontal
        blank=False
    )

    understanding_attempts = models.IntegerField(initial=0)
    understanding_first_try_correct = models.BooleanField(initial=False)

    SM1 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[0], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM2 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[1], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM3 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[2], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SM4 = models.IntegerField(label=C.SURVEY_M_QUESTIONS[3], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    
    SO1 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[0], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO2 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[1], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO3 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[2], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO4 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[3], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO5 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[4], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO6 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[5], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    SO7 = models.IntegerField(label=C.SURVEY_O_QUESTIONS[6], choices=range(1, 6), widget=widgets.RadioSelectHorizontal)
    
    # Big5 questions
    Q1 = models.IntegerField(label=C.QUESTIONS[0], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q2 = models.IntegerField(label=C.QUESTIONS[1], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q3 = models.IntegerField(label=C.QUESTIONS[2], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q4 = models.IntegerField(label=C.QUESTIONS[3], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q5 = models.IntegerField(label=C.QUESTIONS[4], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q6 = models.IntegerField(label=C.QUESTIONS[5], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q7 = models.IntegerField(label=C.QUESTIONS[6], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q8 = models.IntegerField(label=C.QUESTIONS[7], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q9 = models.IntegerField(label=C.QUESTIONS[8], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q10 = models.IntegerField(label=C.QUESTIONS[9], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q11 = models.IntegerField(label=C.QUESTIONS[10], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Q12 = models.IntegerField(label=C.QUESTIONS[11], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    
    # Comparison questions
    Comp1 = models.IntegerField(label=C.COMPARISON_QUESTIONS[0], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp2 = models.IntegerField(label=C.COMPARISON_QUESTIONS[1], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp3 = models.IntegerField(label=C.COMPARISON_QUESTIONS[2], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp4 = models.IntegerField(label=C.COMPARISON_QUESTIONS[3], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp5 = models.IntegerField(label=C.COMPARISON_QUESTIONS[4], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp6 = models.IntegerField(label=C.COMPARISON_QUESTIONS[5], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    Comp7 = models.IntegerField(label=C.COMPARISON_QUESTIONS[6], choices=C.CHOICES, widget=widgets.RadioSelectHorizontal)
    
    # Dictator game
    dictator_keep = models.CurrencyField(
        min=0, 
        max=C.DICTATOR_ENDOWMENT,
        label="(Please move the slider)"
    )
    
    # Demographic fields
    age = models.IntegerField(label=C.AGE_LABEL, min=18, max=100)
    gender = models.StringField(
        label=C.GENDER_LABEL,
        choices=C.GENDER_CHOICES
    )
    education = models.StringField(
        label=C.EDUCATION_LABEL,
        choices=C.EDUCATION_CHOICES
    )
    income = models.StringField(
        label=C.INCOME_LABEL,
        choices=C.INCOME_CHOICES
    )
    employment = models.StringField(
        label=C.EMPLOYMENT_LABEL,
        choices=C.EMPLOYMENT_CHOICES
    )
    occupation = models.StringField(
        label=C.OCCUPATION_LABEL,
        choices=C.OCCUPATION_CHOICES
    )


# Helper functions for working with CSV data
def get_value_from_row(row, column_indices, column_name, default=""):
    """Helper function to get a value from a row using column name"""
    if column_name in column_indices:
        idx = column_indices[column_name]
        if idx < len(row):
            return row[idx]
    return default


# PAGES

class Role(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        manager_data = player.session.vars.get('manager_data', [])
        column_indices = player.session.vars.get('manager_data_columns', {})
        
        if 'used_manager_ids' not in player.session.vars:
            player.session.vars['used_manager_ids'] = []
        
        # Initialize counters for balanced matching
        if 'same_pairs_count' not in player.session.vars:
            player.session.vars['same_pairs_count'] = 0
        if 'different_pairs_count' not in player.session.vars:
            player.session.vars['different_pairs_count'] = 0
        
        used_ids = player.session.vars['used_manager_ids']
        
        print(f"\n{'='*50}")
        print(f"MATCHING PLAYER {player.id_in_group}")
        print(f"{'='*50}")
        print(f"Participant code: {player.participant.code}")
        
        # Check if we have manager data
        if not manager_data:
            print("❌ ERROR: No manager data available")
            player.matched_manager_id = "ERROR_NO_DATA"
            return
        
        # Get column indices
        id_column = column_indices.get('participantid_in_session', -1)
        prefer_column = column_indices.get('main1playerprefer', -1)
        
        if id_column == -1 or prefer_column == -1:
            print("❌ ERROR: Required columns not found")
            player.matched_manager_id = "ERROR_NO_COLUMN"
            return
        
        # Filter available managers
        available_managers = [row for row in manager_data 
                             if row[id_column] not in used_ids]
        
        if not available_managers:
            print("❌ ERROR: No available managers")
            player.matched_manager_id = "ERROR_NO_AVAILABLE"
            return
        
        # Get current balance status
        same_count = player.session.vars['same_pairs_count']
        diff_count = player.session.vars['different_pairs_count']
        balance_gap = same_count - diff_count
        
        print(f"Current balance - Same: {same_count}, Different: {diff_count}, Gap: {balance_gap}")
        
        # Separate available managers by their preference
        managers_left = [m for m in available_managers if m[prefer_column] == 'Left']
        managers_right = [m for m in available_managers if m[prefer_column] == 'Right']
        
        print(f"Available - Left managers: {len(managers_left)}, Right managers: {len(managers_right)}")
        
        # BALANCED MATCHING ALGORITHM
        selected_manager = None
        pair_type = None
        
        # Strategy: maintain balance between same and different pairs
        if balance_gap > 2:  # Too many same pairs
            # Prioritize different pairs
            print("⚖️ Balancing: Need more DIFFERENT pairs")
            # Employee hasn't chosen yet, so we need to wait
            # For now, we'll bias the selection but can't guarantee different
            # We'll implement a probabilistic approach
            
            # Calculate probabilities based on available managers
            total_available = len(available_managers)
            prob_different = min(0.8, 0.5 + (balance_gap * 0.1))  # Increase probability
            
            if random.random() < prob_different:
                # Try to select a manager with opposite preference
                # Since we don't know employee's choice yet, we balance the pool
                # Select from the minority group to increase different pair chances
                if len(managers_left) < len(managers_right):
                    selected_manager = random.choice(managers_left) if managers_left else random.choice(managers_right)
                else:
                    selected_manager = random.choice(managers_right) if managers_right else random.choice(managers_left)
            else:
                selected_manager = random.choice(available_managers)
                
        elif balance_gap < -2:  # Too many different pairs
            # Prioritize same pairs
            print("⚖️ Balancing: Need more SAME pairs")
            
            prob_same = min(0.8, 0.5 + (abs(balance_gap) * 0.1))
            
            if random.random() < prob_same:
                # Select from the majority group to increase same pair chances
                if len(managers_left) > len(managers_right):
                    selected_manager = random.choice(managers_left) if managers_left else random.choice(managers_right)
                else:
                    selected_manager = random.choice(managers_right) if managers_right else random.choice(managers_left)
            else:
                selected_manager = random.choice(available_managers)
                
        else:  # Balanced or close to balanced
            print("✓ Currently balanced, random selection")
            selected_manager = random.choice(available_managers)
        
        # Record the match
        manager_id = selected_manager[id_column]
        player.matched_manager_id = manager_id
        player.group_manager_id = manager_id
        player.manager_match_order = len(used_ids) + 1
        player.manager_match_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✓ Selected manager: {manager_id}")
        
        # Store manager's preference
        player.group_manager_prefer = selected_manager[prefer_column]
        player.group_prefer = player.group_manager_prefer
        
        # Map preference to team
        painting_mapping = {'Left': 'Klee', 'Right': 'Kandinsky'}
        player.group_team = painting_mapping.get(player.group_prefer, "Not assigned")
        
        # Assign organization
        player.group_organization = random.choice(C.CHALLENGE_CHOICES)
        
        # Store manager data
        stated_amount_column = column_indices.get('main1playerstated_amount', -1)
        correct_amount_column = column_indices.get('main1playerbriefing_correct_amou', -1)
        threshold_integer_column = column_indices.get('main1playerthreshold_integer', -1)
        
        if stated_amount_column != -1 and stated_amount_column < len(selected_manager):
            player.manager_stated_amount = selected_manager[stated_amount_column]
        else:
            player.manager_stated_amount = "Not available"
        
        if correct_amount_column != -1 and correct_amount_column < len(selected_manager):
            player.manager_correct_amount = selected_manager[correct_amount_column]
        else:
            player.manager_correct_amount = "Not available"
        
        if threshold_integer_column != -1 and threshold_integer_column < len(selected_manager):
            player.manager_threshold_integer = selected_manager[threshold_integer_column]
        else:
            player.manager_threshold_integer = "8"
        
        # Mark this manager as used
        player.session.vars['used_manager_ids'].append(manager_id)
        
        print(f"✓ MATCHING COMPLETE")
        print(f"{'='*50}\n")


class Painting(Page):
    form_model = 'player'
    form_fields = ['prefer']
    
    @staticmethod
    def vars_for_template(player: Player):
        manager_prefer = player.field_maybe_none('group_manager_prefer') or 'Not available'
        return {
            'manager_prefer': manager_prefer,
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        # After employee makes their choice, determine pair type
        employee_prefer = player.prefer
        manager_prefer = player.group_manager_prefer
        
        if employee_prefer == manager_prefer:
            # Same pair
            player.session.vars['same_pairs_count'] += 1
            pair_type = "SAME"
        else:
            # Different pair
            player.session.vars['different_pairs_count'] += 1
            pair_type = "DIFFERENT"
        
        print(f"\n📊 PAIR TYPE RECORDED: {pair_type}")
        print(f"   Employee: {employee_prefer}, Manager: {manager_prefer}")
        print(f"   Total - Same: {player.session.vars['same_pairs_count']}, Different: {player.session.vars['different_pairs_count']}")
        print(f"   Balance gap: {player.session.vars['same_pairs_count'] - player.session.vars['different_pairs_count']}\n")
    

class Charity(Page):
    pass

class Organization(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'team': player.field_maybe_none('group_team') or 'Not assigned'
        }


class MatchingResult(Page):
    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'player_prefer': player.field_maybe_none('prefer'),
            'group_prefer': player.field_maybe_none('group_prefer')
        }


class BeforeIQTest(Page):
    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }


class MisreportingRule2(Page):
    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'threshold_integer': player.field_maybe_none('manager_threshold_integer') or '8'  # Default to 8 if not found
        }

class Score(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player, timeout_happened=False):
        # Safely get stored manager data with defaults if None
        stated_amount = player.field_maybe_none('manager_stated_amount') or 'Not available'
        correct_amount = player.field_maybe_none('manager_correct_amount') or 'Not available'
        
        
        return {
            'stated_amount': stated_amount,
            'correct_amount': correct_amount,
            'manager_id': player.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }
    
class Understanding(Page):
    form_model = 'player'
    form_fields = ['choiceE','choiceM','choiceT','choiceO']
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }
    
    @staticmethod
    def error_message(player: Player, values):
        # Increment attempts counter
        if player.understanding_attempts is None:
            player.understanding_attempts = 0
        player.understanding_attempts += 1
        
        # Map the preferences to correct answers
        painting_mapping = {
            'Left': 'Klee',
            'Right': 'Kandinsky'
        }
        
        # Get player's own preference
        player_prefer = player.field_maybe_none('prefer')
        if player_prefer:
            correct_choiceE = painting_mapping.get(player_prefer, 'Unknown')
        else:
            correct_choiceE = 'Unknown'
        
        # Get manager's preference (which is also group_prefer)
        manager_prefer = player.field_maybe_none('group_prefer')
        if manager_prefer:
            correct_choiceM = painting_mapping.get(manager_prefer, 'Unknown')
        else:
            correct_choiceM = 'Unknown'
        
        # Get team (already mapped to Klee/Kandinsky)
        correct_choiceT = player.field_maybe_none('group_team') or 'Unknown'
        
        # Get organization
        correct_choiceO = player.field_maybe_none('group_organization') or 'Unknown'
        
        # Debug print
        print(f"\n=== Understanding Check Debug ===")
        print(f"Player ID: {player.id_in_group}")
        print(f"Attempt: {player.understanding_attempts}")
        print(f"Correct E: {correct_choiceE}, Answer: {values.get('choiceE')}")
        print(f"Correct M: {correct_choiceM}, Answer: {values.get('choiceM')}")
        print(f"Correct T: {correct_choiceT}, Answer: {values.get('choiceT')}")
        print(f"Correct O: {correct_choiceO}, Answer: {values.get('choiceO')}")
        
        # Check if all answers are correct
        errors = []
        
        if values.get('choiceE') != correct_choiceE:
            errors.append('Question 1 (Your painting): Incorrect answer.')
        
        if values.get('choiceM') != correct_choiceM:
            errors.append('Question 2 (Manager\'s painting): Incorrect answer.')
        
        if values.get('choiceT') != correct_choiceT:
            errors.append('Question 3 (Team painting): Incorrect answer.')
        
        if values.get('choiceO') != correct_choiceO:
            errors.append('Question 4 (Organization\'s charity): Incorrect answer.')
        
        # If this is the first attempt and all answers are correct, mark it
        if player.understanding_attempts == 1 and len(errors) == 0:
            player.understanding_first_try_correct = True
            print("First try correct!")
        elif len(errors) == 0:
            player.understanding_first_try_correct = False
            print("Correct on later attempt")
        
        print(f"Errors found: {len(errors)}")
        print("=" * 35)
        
        # Return errors if any exist
        if errors:
            error_message = '<strong>Please review your answers. The following questions are incorrect:</strong><br><br>'
            error_message += '<br>'.join(errors)
            error_message += '<br><br><em>Please correct your answers and try again.</em>'
            
            return error_message
        
        # No errors means all correct - allow to proceed
        return None


class Audit(Page):
    form_model = 'player'
    form_fields = ['report_probability']
    @staticmethod
    def vars_for_template(player:Player, timeout_happened=False):
        # Generate a random integer for the reporting mechanism
        player.report_rand_int = random.randint(0, 100)
        
        # Safely get stored manager data with defaults if None
        stated_amount = player.field_maybe_none('manager_stated_amount') or 'Not available'
        correct_amount = player.field_maybe_none('manager_correct_amount') or 'Not available'
        
        
        return {
            'stated_amount': stated_amount,
            'correct_amount': correct_amount,
            'manager_id': player.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }
    @staticmethod
    def before_next_page(player:Player, timeout_happened=False):
        # Determine if the report is successful based on the probability
        if player.report_probability > player.report_rand_int:
            player.report = True
            player.session.vars['report'] = True
        else:
            player.report = False
            player.session.vars['report'] = False


class Survey_m(Page):
    form_model = 'player'
    form_fields = [f'SM{i}' for i in range(1, len(C.SURVEY_M_QUESTIONS) + 1)]
    
    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'player_prefer': player.field_maybe_none('prefer'),
            'group_prefer': player.field_maybe_none('group_prefer')
        }


class Survey_o(Page):
    form_model = 'player'
    form_fields = [f'SO{i}' for i in range(1, len(C.SURVEY_O_QUESTIONS) + 1)]

    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }

class Survey_c(Page):
    form_model = 'player'
    form_fields = ['charity_1', 'charity_2']

    @staticmethod
    def vars_for_template(player: Player):
        
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }

class Big5(Page):
    form_model = 'player'
    form_fields = [f'Q{i + 1}' for i in range(len(C.QUESTIONS))]


class Comparison(Page):
    form_model = 'player'
    form_fields = [f'Comp{i}' for i in range(1, len(C.COMPARISON_QUESTIONS) + 1)]


class Dictator(Page):
    form_model = 'player'
    form_fields = ['dictator_keep']
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'endowment': C.DICTATOR_ENDOWMENT
        }


class Info(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'income', 'employment', 'occupation']


class Result(Page):
    @staticmethod
    def vars_for_template(player: Player):
        report_status = player.session.vars.get('report', False)
        
        # Get manager's stated amount
        try:
            stated_amount = int(player.manager_stated_amount)
        except (ValueError, TypeError):
            stated_amount = 0
        
        # Calculate bonus with maximum cap (£0.37 per point above 8, max £1.5, 4 questions)
        if stated_amount > 8:
            bonus_amount = min((stated_amount - 8) * 0.5, 2)  # Cap at £1.5
        else:
            bonus_amount = 0
        
        # Calculate total payment (base £0.5 + bonus)
        if report_status:
            manager_total_payment = 0.67  # Only base pay
        else:
            manager_total_payment = 0.67 + bonus_amount  # Base + bonus
        
        return {
            'manager_id': player.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'report': report_status,
            'stated_amount': player.manager_stated_amount,
            'correct_amount': player.manager_correct_amount,
            'bonus_amount': f"{bonus_amount:.2f}",
            'manager_total_payment': f"{manager_total_payment:.2f}",
            'player_payoff': player.payoff
        }


page_sequence = [
    Role,
    Painting,
    MatchingResult,
    Charity,
    Survey_c,
    Organization,
    Understanding,
    BeforeIQTest,
    MisreportingRule2,
    Score,
    Audit,
    Survey_m,
    Survey_o,
    Big5, 
    Comparison, 
    Dictator, 
    Info, 
    Result
]