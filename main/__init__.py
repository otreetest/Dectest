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


def creating_session(subsession: Subsession):
    """
    预分配方案：在会话创建时就完成所有经理-员工的匹配
    这样可以完全避免并发问题
    """
    session = subsession.session
    
    # 初始化 session 变量
    session.vars['session_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session.vars['same_pairs_count'] = 0
    session.vars['different_pairs_count'] = 0
    
    # 加载 CSV 数据
    if not os.path.exists(C.MANAGER_DATA_PATH):
        print(f"\n❌ Manager data file not found: {C.MANAGER_DATA_PATH}")
        print(f"   Current directory: {current_dir}")
        print(f"   Please ensure input.csv exists in the correct location")
        return
    
    try:
        # 读取 CSV
        manager_data = []
        header = []
        with open(C.MANAGER_DATA_PATH, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)
            for row in csv_reader:
                manager_data.append(row)
        
        column_indices = {name: idx for idx, name in enumerate(header)}
        
        # 获取所有玩家
        players = subsession.get_players()
        num_players = len(players)
        num_managers = len(manager_data)
        
        print(f"\n{'='*50}")
        print(f"SESSION INITIALIZATION - PRE-ALLOCATION")
        print(f"{'='*50}")
        print(f"Session code: {session.code}")
        print(f"Session start: {session.vars['session_start_time']}")
        print(f"Players in session: {num_players}")
        print(f"Managers available: {num_managers}")
        print(f"CSV columns: {header}")
        
        if num_managers < num_players:
            print(f"\n⚠️  WARNING: Not enough managers!")
            print(f"   Need: {num_players}")
            print(f"   Have: {num_managers}")
            print(f"   Shortage: {num_players - num_managers}")
            print(f"\n   Proceeding with available managers...")
        else:
            print(f"\n✓ Sufficient managers available")
            print(f"  Surplus: {num_managers - num_players}")
        
        # 关键列索引
        id_column = column_indices.get('participantid_in_session', -1)
        prefer_column = column_indices.get('main1playerprefer', -1)
        stated_column = column_indices.get('main1playerstated_amount', -1)
        correct_column = column_indices.get('main1playerbriefing_correct_amou', -1)
        threshold_column = column_indices.get('main1playerthreshold_integer', -1)
        
        if id_column == -1 or prefer_column == -1:
            print("❌ ERROR: Required columns not found in CSV")
            return
        
        # 分离 Left 和 Right 经理
        managers_left = [m for m in manager_data if m[prefer_column] == 'Left']
        managers_right = [m for m in manager_data if m[prefer_column] == 'Right']
        
        print(f"\nManager distribution:")
        print(f"  Left preference: {len(managers_left)}")
        print(f"  Right preference: {len(managers_right)}")
        
        # 打乱两组经理
        random.shuffle(managers_left)
        random.shuffle(managers_right)
        
        # 平衡分配策略：交替分配 Left 和 Right 经理
        assigned_managers = []
        left_idx = 0
        right_idx = 0
        
        for i in range(num_players):
            # 交替分配，确保平衡
            if i % 2 == 0:
                # 优先分配 Left
                if left_idx < len(managers_left):
                    assigned_managers.append(managers_left[left_idx])
                    left_idx += 1
                elif right_idx < len(managers_right):
                    assigned_managers.append(managers_right[right_idx])
                    right_idx += 1
            else:
                # 优先分配 Right
                if right_idx < len(managers_right):
                    assigned_managers.append(managers_right[right_idx])
                    right_idx += 1
                elif left_idx < len(managers_left):
                    assigned_managers.append(managers_left[left_idx])
                    left_idx += 1
        
        # 分配给每个玩家
        painting_mapping = {'Left': 'Klee', 'Right': 'Kandinsky'}
        
        for i, player in enumerate(players):
            if i < len(assigned_managers):
                manager_row = assigned_managers[i]
                
                # 提取经理数据
                manager_id = manager_row[id_column]
                manager_prefer = manager_row[prefer_column]
                
                # 安全提取其他字段
                def get_value(col_idx, default="Not available"):
                    if col_idx != -1 and col_idx < len(manager_row):
                        return manager_row[col_idx]
                    return default
                
                manager_stated = get_value(stated_column)
                manager_correct = get_value(correct_column)
                manager_threshold = get_value(threshold_column, "8")
                
                # 存储到 participant.vars（跨 app 持久化）
                player.participant.vars['assigned_manager'] = {
                    'id': manager_id,
                    'prefer': manager_prefer,
                    'team': painting_mapping.get(manager_prefer, "Not assigned"),
                    'organization': random.choice(C.CHALLENGE_CHOICES),
                    'stated_amount': manager_stated,
                    'correct_amount': manager_correct,
                    'threshold_integer': manager_threshold,
                    'assignment_order': i + 1,
                    'assignment_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f"✓ Player {i+1} assigned Manager {manager_id} (Prefer: {manager_prefer})")
            else:
                print(f"❌ Player {i+1} could not be assigned (no managers left)")
        
        print(f"\n{'='*50}")
        print(f"PRE-ALLOCATION COMPLETE")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"\n❌ Error during pre-allocation: {e}")
        import traceback
        traceback.print_exc()


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
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    choiceM = models.CharField(
        label="2) Please indicate the painting that <b>your manager selected </b>at the beginning of the game:<br>",
        choices=["Klee", "Kandinsky"],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    choiceT = models.CharField(
        label="3) Please indicate the painting that <b>represented your team</b>:<br>",
        choices=["Klee", "Kandinsky"],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    choiceO = models.CharField(
        label="<br><img src='/static/img/RedCross.png' style='width: 160px; max-width: 100%;'>  <img src='/static/img/NRA.png' style='width: 160px; max-width: 100%;'><br><br>4) Please indicate the charity that your <b>organization donated to</b>:<br>",
        choices=["Red Cross", "NRA"],
        widget=widgets.RadioSelectHorizontal,
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


# PAGES

class Role(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        """
        从 participant.vars 中读取预分配的经理数据
        不再进行动态分配，完全避免并发问题
        """
        assigned = player.participant.vars.get('assigned_manager')
        
        if not assigned:
            print(f"❌ ERROR: Player {player.id_in_group} has no assigned manager")
            player.matched_manager_id = "ERROR_NO_ASSIGNMENT"
            return
        
        # 直接读取预分配的数据
        player.matched_manager_id = assigned['id']
        player.group_manager_id = assigned['id']
        player.group_manager_prefer = assigned['prefer']
        player.group_prefer = assigned['prefer']
        player.group_team = assigned['team']
        player.group_organization = assigned['organization']
        
        player.manager_stated_amount = assigned['stated_amount']
        player.manager_correct_amount = assigned['correct_amount']
        player.manager_threshold_integer = assigned['threshold_integer']
        
        player.manager_match_order = assigned['assignment_order']
        player.manager_match_timestamp = assigned['assignment_timestamp']
        
        print(f"\n{'='*50}")
        print(f"LOADING PRE-ASSIGNED MANAGER FOR PLAYER {player.id_in_group}")
        print(f"{'='*50}")
        print(f"Manager ID: {player.matched_manager_id}")
        print(f"Manager Preference: {player.group_manager_prefer}")
        print(f"Team: {player.group_team}")
        print(f"Organization: {player.group_organization}")
        print(f"Assignment Order: {player.manager_match_order}")
        print(f"{'='*50}\n")


class Painting(Page):
    form_model = 'player'
    form_fields = ['prefer']
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'manager_prefer': player.field_maybe_none('group_manager_prefer') or 'Not available',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        """
        员工选择后，记录配对类型
        这里的计数更新仍有轻微竞态风险，但不影响核心分配逻辑
        如需完全避免，可以在 Result 页面统一计算
        """
        employee_prefer = player.prefer
        manager_prefer = player.group_manager_prefer
        
        if employee_prefer == manager_prefer:
            player.session.vars['same_pairs_count'] += 1
            pair_type = "SAME"
        else:
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
            'threshold_integer': player.field_maybe_none('manager_threshold_integer') or '8'
        }


class Score(Page):
    form_model = 'player'
    
    @staticmethod
    def vars_for_template(player: Player, timeout_happened=False):
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
    form_fields = ['choiceE', 'choiceM', 'choiceT', 'choiceO']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }

    @staticmethod
    def error_message(player: Player, values):
        if player.understanding_attempts is None:
            player.understanding_attempts = 0
        player.understanding_attempts += 1

        painting_mapping = {'Left': 'Klee', 'Right': 'Kandinsky'}
        
        p_pref = player.field_maybe_none('prefer')
        m_pref = player.field_maybe_none('group_prefer')
        g_team = player.field_maybe_none('group_team')
        g_org  = player.field_maybe_none('group_organization')

        if not all([p_pref, m_pref, g_team, g_org]):
            return "Error: Missing group assignment data. Please refresh or contact support."

        correct_answers = {
            'choiceE': painting_mapping.get(p_pref),
            'choiceM': painting_mapping.get(m_pref),
            'choiceT': g_team,
            'choiceO': g_org
        }

        field_labels = {
            'choiceE': 'Question 1 (Your painting)',
            'choiceM': 'Question 2 (Manager\'s painting)',
            'choiceT': 'Question 3 (Team painting)',
            'choiceO': 'Question 4 (Organization\'s charity)'
        }

        errors = []
        for field, correct_val in correct_answers.items():
            if values.get(field) != correct_val:
                errors.append(field_labels[field])

        if not errors:
            if player.understanding_attempts == 1:
                player.understanding_first_try_correct = True
            return None
        else:
            if player.understanding_attempts == 1:
                player.understanding_first_try_correct = False
                
            error_html = '<strong>Some answers are incorrect:</strong><ul style="margin-top: 5px;">'
            for e in errors:
                error_html += f'<li>{e}</li>'
            error_html += '</ul><em>Please review the instructions and correct your choices.</em>'
            
            return error_html


class Audit(Page):
    form_model = 'player'
    form_fields = ['report_probability']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'stated_amount': player.field_maybe_none('manager_stated_amount') or 'Not available',
            'correct_amount': player.field_maybe_none('manager_correct_amount') or 'Not available',
            'manager_id': player.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned'
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        player.report_rand_int = random.randint(0, 100)
        
        if player.report_probability > player.report_rand_int:
            player.report = True
        else:
            player.report = False


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
        # 核心修复：从 player.report 获取状态，而非 session.vars
        report_status = player.report 
        
        try:
            stated_amount = int(player.manager_stated_amount)
        except (ValueError, TypeError):
            stated_amount = 0
        
        # 这里的计算逻辑建议根据你的实验手册核对
        if stated_amount > 8:
            bonus_amount = min((stated_amount - 8) * 0.5, 2.0)
        else:
            bonus_amount = 0.0
        
        # 根据举报状态决定经理支付（此处逻辑仅供数据展示）
        if report_status:
            manager_total_payment = 0.67 
        else:
            manager_total_payment = 0.67 + bonus_amount
        
        return {
            'report': report_status,
            'bonus_amount': f"{bonus_amount:.2f}",
            'manager_total_payment': f"{manager_total_payment:.2f}",
            'manager_id': player.field_maybe_none('matched_manager_id') or 'Not matched',
            'team': player.field_maybe_none('group_team') or 'Not assigned',
            'organization': player.field_maybe_none('group_organization') or 'Not assigned',
            'stated_amount': player.manager_stated_amount,
            'correct_amount': player.manager_correct_amount,
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