import os
import sys

from random import randint
from functools import partial
from bisect import bisect

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QRadioButton, 
                             QTabWidget, QComboBox, QListWidget, QGroupBox, 
                             QAbstractItemView, QMessageBox, QFileDialog, 
                             QDialog, QScrollArea)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer

import powerlists


################### SETUP GUI ###################
#MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Setup parameters of the main window
        self.setWindowTitle("Marvel Super Heroes Character Generator")
        self.setFixedSize(1100, 800)
        self.setWindowIcon(QIcon(resource_path('images/UPB_sm.jpg')))

        #create the menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("&Help")
        self.instruction_action = QAction("&Instructions", self)
        help_menu.addAction(self.instruction_action)
        self.about_action = QAction("&About", self)
        help_menu.addAction(self.about_action)
        options_menu = menu.addMenu("&Options")
        self.std_rank_scores_action = QAction("&Use Standard Rank Scores", self, 
                                         checkable=True)
        options_menu.addAction(self.std_rank_scores_action)
        self.std_rank_scores_action.triggered.connect(self.toggle_std_rank)
        self.instruction_action.triggered.connect(self.show_instructions)
        self.about_action.triggered.connect(self.show_about)

        #Create the labels and text boxes at the top of the window
        self.name_label = QLabel("Name:", self)
        self.name_textbox = QLineEdit(self)

        self.identity_label = QLabel("   Identity:", self)
        self.identity_textbox = QLineEdit(self)
        
        self.sex_label = QLabel("   Sex:", self)
        self.sex_combobox = QComboBox(self)
        self.sex_combobox.setFixedSize(80,30)
        self.sex_combobox.addItems(["", "Female", "Male", "Other"])
        self.sex_combobox.setCurrentText("")

        self.age_label = QLabel("  Age:", self)
        self.age_textbox = QLineEdit(self)
        self.age_textbox.setFixedSize(80,30)

        self.public_radio = QRadioButton("Public", self)
        self.secret_radio = QRadioButton("Secret", self)

        self.group_label = QLabel("Group Affiliation:", self)
        self.group_textbox = QLineEdit(self)

        self.base_label = QLabel("        Base of Operations:", self)
        self.base_textbox = QLineEdit(self)

        #Create the tabs
        self.tab_widget = QTabWidget()
        self.physical_form = QWidget()
        self.abilities_tab = QWidget()
        self.powers_tab = QWidget()
        self.talents_tab = QWidget()
        self.contacts_tab = QWidget()
        self.tab_widget.addTab(self.physical_form, "Physical Form")
        self.tab_widget.addTab(self.abilities_tab, "Abilities")
        self.tab_widget.addTab(self.powers_tab, "Powers")
        self.tab_widget.addTab(self.talents_tab, "Talents")
        self.tab_widget.addTab(self.contacts_tab, "Contacts")

        #Create the save and exit buttons
        self.save_button = QPushButton("💾 Save", self)
        self.exit_button = QPushButton("🟥 Exit", self)
        self.save_button.setFixedSize(150,50)
        self.exit_button.setFixedSize(150,50)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.exit_button.clicked.connect(self.exit_button_clicked)

        #define variables
        self.clear_info()

        self.physicalforms = {"Normal Human": 2,"Mutant-Induced": 1,"Mutant-Random": 1, 
                             "Mutant-Breed": 1,"Android": 4,"Humanoid Race": 5,
                             "Surgical Composite": 2,"Modified Human-Organic": 1,
                             "Modified Human-Muscular": 1,"Modified Human-Skeletal": 1,
                             "Modified Human-Extra Parts": 1,"Demihuman-Centaur": 5,
                             "Demihuman-Equiman": 3,"Demihuman-Faun": 2,
                             "Demihuman-Felinoid": 1,"Demihuman-Lupinoid": 4,
                             "Demihuman-Avian": {"Angelic": 3, "Harpy": 2},
                             "Demihuman-Chiropteran": 2,"Demihuman-Lamian": 3,
                             "Demihuman-Merhuman": 2,"Demihuman-Other": 3,
                             "Cyborg-Artificial limbs/organs": 4,"Cyborg-Exoskeleton": 4,
                             "Cyborg-Mechanical Body": 4,"Cyborg-Mechanically Augmented": 3,
                             "Robot-Human Shape": 4,"Robot-Usuform": 4,"Robot-Metamorphic": 4,
                             "Robot-Computer": 4,"Angel/Demon": 5,"Deity": 5,
                             "Animal": {"Terrestrial": 1, "Extraterrestrial": 5},
                             "Vegetable": 1,"Abnormal Chemistry": 2,"Mineral": 2,
                             "Gaseous": 5,"Liquid": 5,"Energy": 5,"Ethereal": 1,
                             "Undead": 1,"Compound": 0,"Changeling": 5,"Collective Mass": 1}
        
        self.abilities = ["Fighting","Agility","Strength","Endurance","Reason",
                          "Intuition","Psyche","Resources","Popularity"]
        
        self.ranks = ["Shift 0","Feeble","Poor","Typical","Good", "Excellent", 
                      "Remarkable", "Incredible", "Amazing", "Monstrous", 
                      "Unearthly", "Shift X", "Shift Y", "Shift Z", "Class 1000",
                      "Class 3000", "Class 5000", "Beyond"]
        
        self.rank_scores = {"Shift 0": [0,0], "Feeble": [1,2], "Poor": [3,4], 
                            "Typical": [5,6], "Good": [8,10], "Excellent": [16,20],
                            "Remarkable": [26,30], "Incredible": [36,40], 
                            "Amazing": [46,50], "Monstrous": [63,75], 
                            "Unearthly": [88,100], "Shift X": [126,150], 
                            "Shift Y": [176,200], "Shift Z": [351,500], 
                            "Class 1000": [1000,1000], "Class 3000": [3000,3000],
                            "Class 5000": [5000,5000], "Beyond": [10000,10000]}
        
        

        self.initUI()



    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #create main layout
        foundation = QVBoxLayout()
        identity_layout = QHBoxLayout()
        radiobuttons_layout = QHBoxLayout()
        group_layout = QHBoxLayout()
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setSpacing(700)

        #add widgets to the layouts
        identity_layout.addWidget(self.name_label)
        identity_layout.addWidget(self.name_textbox)
        identity_layout.addWidget(self.identity_label)
        identity_layout.addWidget(self.identity_textbox)
        identity_layout.addWidget(self.sex_label)
        identity_layout.addWidget(self.sex_combobox)
        identity_layout.addWidget(self.age_label)
        identity_layout.addWidget(self.age_textbox)
        group_layout.addWidget(self.group_label)
        group_layout.addWidget(self.group_textbox)
        group_layout.addWidget(self.base_label)
        group_layout.addWidget(self.base_textbox)
        radiobuttons_layout.addWidget(self.public_radio)
        radiobuttons_layout.addWidget(self.secret_radio)
        radiobuttons_layout.setAlignment(Qt.AlignHCenter)
        bottom_buttons_layout.addWidget(self.save_button)
        bottom_buttons_layout.addWidget(self.exit_button)

        #add the name and group layouts to the foundation layout
        central_widget.setLayout(foundation)
        foundation.addLayout(identity_layout)
        foundation.addLayout(radiobuttons_layout)
        foundation.addLayout(group_layout)
        foundation.setAlignment(Qt.AlignTop)

        #add the tab widget to the foundation and create layouts for the tabs
        foundation.addWidget(self.tab_widget)
        self.setup_physical_form_tab()
        self.setup_abilities_tab()
        self.setup_powers_tab()
        self.setup_talents_tab()
        self.setup_contacts_tab()

        #add the save and exit buttons to the bottom
        foundation.addLayout(bottom_buttons_layout)


        #apply a style sheet
        self.setStyleSheet("""
            QWidget{
                font-family: "Comic Sans MS";
            }
            QLabel, QTabWidget{
                font-size: 16px;
            }
            QPushButton{
                font-size: 18px;
            }
            QPushButton:focus {
                border: 2px solid #0078d4;
                background-color: #e6f7ff;
            }
            QRadioButton{
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QListWidget{
                font-size: 14px;
                border: 2px inset gray;
            }
            QListWidget:focus {
                border: 2px solid #0078d4;
                background-color: #e6f7ff;
            }
            QComboBox{
                background-color: white; 
                font-size: 14px;
            }
            """)
        
        
    #create the Physical Form tab
    def setup_physical_form_tab(self):
        #create layouts of the tab
        physical_form_tab_layout = QVBoxLayout()
        pf_top_layout = QHBoxLayout()
        pf_notes_layout = QVBoxLayout()
        pf_list_layout = QVBoxLayout()
        pf_origin_layout = QVBoxLayout()
        pf_bonuses_penalties_layout = QGridLayout()


        #add the Physical Form list box and label to the first column
        physical_form_label = QLabel("Physical Form:")
        self.physical_form_list = QListWidget()
        self.physical_form_list.setFixedSize(250,360)
        for physicalform in self.physicalforms:
            self.physical_form_list.addItem(physicalform)

        pf_list_layout.addWidget(physical_form_label)
        pf_list_layout.addWidget(self.physical_form_list)

        self.physical_form_list.setSelectionMode(QAbstractItemView.SingleSelection)

        #connect physical form list click and activate signals to action
        #origin should be re-rolled each time an item is clicked, even if the same item
        #origin also re-rolled if pressing Enter on an item, even if the same item
        self.physical_form_list.itemClicked.connect(self.physical_form_list_selected)
        self.physical_form_list.itemActivated.connect(self.physical_form_list_selected)


        #add the random button and origin boxes to the second column
        origin_spacer = QLabel("")
        origin_spacer.setFixedSize(120,25)
        self.random_pf_button = QPushButton("< Random 🎲", self)
        self.random_pf_button.setFixedSize(120,40)
        origin_label = QLabel("Origin of Power:")
        origin_label.setAlignment(Qt.AlignBottom)
        self.origin_textbox = QLineEdit()
        self.setupTextBox(self.origin_textbox, 260, 30, align=0)
        options_label = QLabel("Physical Form Options:")
        options_label.setAlignment(Qt.AlignBottom)
        self.options_list = QListWidget()
        self.options_list.setFixedSize(260,90)
        compound_label = QLabel("Changeling/Compound Forms:")
        compound_label.setAlignment(Qt.AlignBottom)
        self.compound_list = QListWidget()
        self.compound_list.setFixedSize(260,90)

        self.options_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.compound_list.setSelectionMode(QAbstractItemView.SingleSelection)
        #connect physical form random button click signal and action
        self.random_pf_button.clicked.connect(self.physical_form_random)
        #connect option list click and Enter key signal and action
        self.options_list.itemClicked.connect(self.options_list_selected)
        self.options_list.itemActivated.connect(self.options_list_selected)
        #connect compound list click and Enter key signal and action
        self.compound_list.itemClicked.connect(self.compound_list_selected)
        self.compound_list.itemActivated.connect(self.compound_list_selected)

        #add the widgets to the origin of power column
        pf_origin_layout.addWidget(origin_spacer)
        pf_origin_layout.addWidget(self.random_pf_button)
        pf_origin_layout.addWidget(origin_label)
        pf_origin_layout.addWidget(self.origin_textbox)
        pf_origin_layout.addWidget(options_label)
        pf_origin_layout.addWidget(self.options_list)
        pf_origin_layout.addWidget(compound_label)
        pf_origin_layout.addWidget(self.compound_list)

        pf_origin_layout.setAlignment(Qt.AlignBottom)


        #add the bonuses, penalties and weaknesses boxes to the last column
        self.watcher_image = QLabel()
        self.watcher_pixmap = QPixmap(resource_path('images/watcher.jpg'))
        self.watcher_image.setPixmap(self.watcher_pixmap)
        self.watcher_image.setFixedSize(500,65)
        bonuses_label = QLabel("Bonuses:")
        self.bonuses_textbox = QTextEdit()
        self.setupTextBox(self.bonuses_textbox, 260, 110, align=0)
        bonuses_label.setAlignment(Qt.AlignBottom)

        penalties_label = QLabel("Penalties:")
        self.penalties_textbox = QTextEdit()
        self.setupTextBox(self.penalties_textbox, 260, 110, align=0)
        penalties_label.setAlignment(Qt.AlignBottom)

        weakness_label = QLabel("Weaknesses:")
        weakness_label.setAlignment(Qt.AlignBottom)
        self.weakness_textbox = QTextEdit()
        self.setupTextBox(self.weakness_textbox, 520, 130, align=0)

        pf_bonuses_penalties_layout.addWidget(self.watcher_image,0,0,1,2)
        pf_bonuses_penalties_layout.addWidget(bonuses_label,1,0)
        pf_bonuses_penalties_layout.addWidget(self.bonuses_textbox,2,0)
        pf_bonuses_penalties_layout.addWidget(penalties_label,1, 1)
        pf_bonuses_penalties_layout.addWidget(self.penalties_textbox,2,1)
        pf_bonuses_penalties_layout.addWidget(weakness_label,3,0)
        pf_bonuses_penalties_layout.addWidget(self.weakness_textbox,4,0,4,2)

        pf_bonuses_penalties_layout.setAlignment(Qt.AlignBottom)

        
        #add notes label and box to the bottom of the physical forms tab
        notes_label = QLabel("Notes:")
        self.notes_textbox = QTextEdit()
        notes_label.setAlignment(Qt.AlignBottom)
        self.setupTextBox(self.notes_textbox, 1055, 120, align=0)
        pf_notes_layout.addWidget(notes_label)
        pf_notes_layout.addWidget(self.notes_textbox)


        #add the columns to the top layout
        pf_top_layout.addLayout(pf_list_layout)
        pf_top_layout.addLayout(pf_origin_layout)
        pf_top_layout.addLayout(pf_bonuses_penalties_layout)

        #add the top layout and notes to the main layout of the tab
        physical_form_tab_layout.addLayout(pf_top_layout)
        physical_form_tab_layout.addLayout(pf_notes_layout)

        #apply the main layout to the tab
        self.physical_form.setLayout(physical_form_tab_layout)



    #Create the Abilities tab
    def setup_abilities_tab(self):
        abilities = ["fighting","agility","strength","endurance",
                     "reason","intuition","psyche",""]
        
        #create layouts of the tab
        abilities_tab_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        primary_layout = QVBoxLayout()
        secondary_layout = QGridLayout()

        #create the Table layout
        #create the image
        self.cap_image = QLabel()
        self.cap_pixmap = QPixmap("")
        self.cap_image.setFixedSize(270,140)

        #create the Table label and text box
        table_label = QLabel("Table")
        self.table_text_box = QLineEdit()
        self.setupTextBox(self.table_text_box, 80, 30, align=1)

        #create Table group box
        table_group_box = QGroupBox("")
        table_group_layout = QGridLayout()
        table_group_box.setLayout(table_group_layout)

        table_roll_label = QLabel("Roll")
        table_roll_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        table_rank_label = QLabel("Rank")
        table_rank_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        table_bonus_penalty_label = QLabel("Bonus /\nPenalty")
        table_bonus_penalty_label.setStyleSheet("font-size: 14px;")
        table_bonus_penalty_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        table_group_layout.addWidget(table_roll_label, 0, 0)
        table_group_layout.addWidget(table_rank_label, 0, 1)
        table_group_layout.addWidget(table_bonus_penalty_label, 0, 2)


        #create the Primary Abilities layout
        #create the image and button
        self.ironman_image = QLabel()
        self.ironman_pixmap = QPixmap("")
        self.ironman_image.setFixedSize(350,140)
        self.abilities_button = QPushButton("🎲 Roll Abilities\nv")
        self.abilities_button.setFixedSize(150,60)
        self.abilities_button.setEnabled(False)

        #configure click signal for the Roll Abilities button
        self.abilities_button.clicked.connect(self.roll_abilities)

        #create Abilities group box
        abilities_group_box = QGroupBox("")
        abilities_group_layout = QGridLayout()
        abilities_group_box.setLayout(abilities_group_layout)

        abilities_rank_label = QLabel("Rank")
        abilities_rank_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        abilities_rank_number_label = QLabel("Rank\nNumber")
        abilities_rank_number_label.setStyleSheet("font-size: 14px;")
        abilities_rank_number_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        abilities_group_layout.addWidget(abilities_rank_label,0,1)
        abilities_group_layout.addWidget(abilities_rank_number_label,0,2)


        #create dictionary {ability: {roll,rank,bonus},...}
        self.ability_inputs = {}
        for i, ability in enumerate(abilities, start=1):
            # Create QLineEdit widgets dynamically
            # add a space at the bottom
            if ability == "":
                table_spacer_label = QLabel(ability)
                table_spacer_label.setFixedSize(30,30)
                table_group_layout.addWidget(table_spacer_label, i, 0)
                ability_spacer_label = QLabel(ability)
                ability_spacer_label.setFixedSize(30,30)
                abilities_group_layout.addWidget(ability_spacer_label, i, 0)
            else:
                roll_textbox = QLineEdit()
                rank_roll_textbox = QLineEdit()
                bonus_textbox = QLineEdit()
                self.setupTextBox(roll_textbox, 40, 30, align=1)
                self.setupTextBox(bonus_textbox, 40, 30, align=1)
                self.setupTextBox(rank_roll_textbox, 140, 30, align=1)
                
                ability_name_label = QLabel(ability.capitalize())
                ability_name_label.setStyleSheet("font-size: 20px;")
                abilities_group_layout.addWidget(ability_name_label, i, 0)
                rank_textbox = QLineEdit()
                rank_number_textbox = QLineEdit()
                bonus_rank_button = QPushButton("+")
                self.setupTextBox(rank_textbox, 140, 30, align=1)
                self.setupTextBox(rank_number_textbox, 40, 30, align=1)
                bonus_rank_button.setFixedSize(30,30)
                bonus_rank_button.setEnabled(False)
                #setup connection between each bonus button and its click signal
                bonus_rank_button.clicked.connect(partial(self.bonus_ability_clicked, ability))

                #Store in dictionary using the ability name as the key
                self.ability_inputs[ability] = {
                    "roll": roll_textbox,
                    "rank_roll": rank_roll_textbox,
                    "bonus": bonus_textbox,
                    "rank": rank_textbox,
                    "score": rank_number_textbox,
                    "bonus_button": bonus_rank_button
                }

                # Add widgets to layout
                table_group_layout.addWidget(roll_textbox, i, 0)
                table_group_layout.addWidget(rank_roll_textbox, i, 1)
                table_group_layout.addWidget(bonus_textbox, i, 2)

                abilities_group_layout.addWidget(rank_textbox, i, 1)
                abilities_group_layout.addWidget(rank_number_textbox, i, 2, 
                                                 alignment=Qt.AlignHCenter)
                abilities_group_layout.addWidget(bonus_rank_button, i, 3)

        
        # Add the image, button and group box to the table layout
        table_layout.addWidget(self.cap_image)
        table_layout.addWidget(table_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)
        table_layout.addWidget(self.table_text_box, alignment=Qt.AlignHCenter)
        table_layout.addWidget(table_group_box)

        # Add the image, button and group box to the primary layout
        primary_layout.addWidget(self.ironman_image)
        primary_layout.addWidget(self.abilities_button, 
                                 alignment=Qt.AlignHCenter | Qt.AlignBottom)
        primary_layout.addWidget(abilities_group_box, alignment=Qt.AlignCenter)


        #create the Secondary layout
        #create the images
        self.bubble_image = QLabel()
        self.bubble_pixmap = QPixmap("")
        self.bubble_image.setPixmap(self.bubble_pixmap)
        self.bubble_image.setFixedSize(155,205)
        self.blackpanther_image = QLabel()
        self.blackpanther_pixmap = QPixmap("")
        self.blackpanther_image.setPixmap(self.blackpanther_pixmap)
        self.blackpanther_image.setFixedSize(250,305)

        #create Secondary group box
        secondary_group_box = QGroupBox("")
        secondary_group_layout = QGridLayout()
        secondary_group_box.setLayout(secondary_group_layout)

        #create separate box for the resource and popularity roll boxes
        res_pop_roll_group_box = QGroupBox("")
        res_pop_roll_group_layout = QGridLayout()
        res_pop_roll_group_box.setLayout(res_pop_roll_group_layout)

        #create Health and Karma labels and textboxes
        health_label = QLabel("Health:")
        health_label.setStyleSheet("font-size: 14px;")
        self.health_textbox = QLineEdit()
        self.health_textbox.setReadOnly(True)
        self.health_textbox.setFixedSize(80, 30)
        self.health_textbox.setAlignment(Qt.AlignCenter)
        karma_label = QLabel("Karma:")
        karma_label.setStyleSheet("font-size: 14px;")
        self.karma_textbox = QLineEdit()
        self.karma_textbox.setReadOnly(True)
        self.karma_textbox.setFixedSize(80,30)
        self.karma_textbox.setAlignment(Qt.AlignCenter)

        #create Secondary Abilities labels
        resources_label = QLabel("Resources:")
        resources_label.setStyleSheet("font-size: 14px;")
        resources_label.setAlignment(Qt.AlignBottom)
        popularity_label = QLabel("Popularity:")
        popularity_label.setStyleSheet("font-size: 14px;")
        secondary_roll_label = QLabel("Roll")
        secondary_roll_label.setStyleSheet("font-size: 14px;")
        secondary_roll_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        secondary_rank_label = QLabel("Rank")
        secondary_rank_label.setStyleSheet("font-size: 14px;")
        secondary_rank_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        secondary_bonus_penalty_label = QLabel("Bonus /\nPenalty")
        secondary_bonus_penalty_label.setStyleSheet("font-size: 12px;")
        secondary_bonus_penalty_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)

        #create dictionary {ability: {roll,rank,bonus},...}
        secondary_abilities = ["resources","","popularity"," "]
        self.secondary_ability_inputs = {}
        for i, ability in enumerate(secondary_abilities, start=1):
            if ability == "":
                res_pop_spacer_label1 = QLabel(ability)
                res_pop_spacer_label1.setFixedSize(30,55)
                res_pop_roll_group_layout.addWidget(res_pop_spacer_label1, 6, 1)
            if ability == " ":
                res_pop_spacer_label2 = QLabel(ability)
                res_pop_spacer_label2.setFixedSize(30,30)
                res_pop_roll_group_layout.addWidget(res_pop_spacer_label2, 10, 1)
            else:
                self.secondary_rank_textbox = QLineEdit()
                self.setupTextBox(self.secondary_rank_textbox, 140, 30, align=1)
                self.secondary_score_textbox = QLineEdit()
                self.setupTextBox(self.secondary_score_textbox, 40, 30, align=1)

                #add Secondary roll boxes
                secondary_roll_textbox = QLineEdit()
                self.setupTextBox(secondary_roll_textbox, 40, 30, align=1)
                secondary_roll_rank_text_box = QLineEdit()
                self.setupTextBox(secondary_roll_rank_text_box, 140, 30, align=1)
                secondary_roll_bp_text_box = QLineEdit()
                self.setupTextBox(secondary_roll_bp_text_box, 40, 30, align=1)

                #Store in dictionary using the ability name as the key
                self.secondary_ability_inputs[ability] = {
                    "roll": secondary_roll_textbox,
                    "rank_roll": secondary_roll_rank_text_box,
                    "bonus": secondary_roll_bp_text_box,
                    "rank": self.secondary_rank_textbox,
                    "score": self.secondary_score_textbox,
                }
                #add textboxes only for the abilities and not the empty strings in the list
                if ability == "resources":
                    secondary_group_layout.addWidget(self.secondary_rank_textbox, 5, 0)
                    secondary_group_layout.addWidget(self.secondary_score_textbox, 6, 0)
                    res_pop_roll_group_layout.addWidget(secondary_roll_textbox, 5, 1)
                    res_pop_roll_group_layout.addWidget(secondary_roll_rank_text_box, 5, 2)
                    res_pop_roll_group_layout.addWidget(secondary_roll_bp_text_box, 5, 3)
                if ability == "popularity":
                    secondary_group_layout.addWidget(self.secondary_rank_textbox, 8, 0)
                    secondary_group_layout.addWidget(self.secondary_score_textbox, 9, 0)
                    res_pop_roll_group_layout.addWidget(secondary_roll_textbox, 8, 1)
                    res_pop_roll_group_layout.addWidget(secondary_roll_rank_text_box, 8, 2)
                    res_pop_roll_group_layout.addWidget(secondary_roll_bp_text_box, 8, 3)


        secondary_group_layout.addWidget(health_label, 0, 0)
        secondary_group_layout.addWidget(self.health_textbox, 1, 0)
        secondary_group_layout.addWidget(karma_label, 2, 0)
        secondary_group_layout.addWidget(self.karma_textbox, 3, 0)
        secondary_group_layout.addWidget(resources_label, 4, 0)
        secondary_group_layout.addWidget(popularity_label, 7, 0)
        res_pop_roll_group_layout.addWidget(secondary_roll_label, 4, 1)
        res_pop_roll_group_layout.addWidget(secondary_rank_label, 4, 2)
        res_pop_roll_group_layout.addWidget(secondary_bonus_penalty_label, 4, 3)
        
        secondary_layout.addWidget(self.bubble_image, 0, 0)
        secondary_layout.addWidget(self.blackpanther_image, 0, 1, 2, 1)
        secondary_layout.addWidget(secondary_group_box, 3, 0, 3, 1, 
                                   alignment=Qt.AlignHCenter | Qt.AlignBottom)
        secondary_layout.addWidget(res_pop_roll_group_box, 3, 1, 3, 1,
                                   alignment=Qt.AlignHCenter | Qt.AlignBottom)


        #add the three layouts to the main layout of the tab
        abilities_tab_layout.addLayout(table_layout)
        abilities_tab_layout.addLayout(primary_layout)
        abilities_tab_layout.addLayout(secondary_layout)


        #apply the main layout to the tab
        self.abilities_tab.setLayout(abilities_tab_layout)



    def setup_powers_tab(self):
        powers_tab_layout = QGridLayout()
        buy_remove_powers_layout = QHBoxLayout()

        self.roll_power_classes_button = QPushButton("🎲 Roll Power Classes\nv")
        self.roll_power_classes_button.setFixedSize(200,60)
        self.roll_power_classes_button.setEnabled(False)
        #configure click signal for the Roll Power Classes button
        self.roll_power_classes_button.clicked.connect(self.roll_power_classes)

        power_classes_label = QLabel("Power Classes:")
        self.power_classes_listbox = QListWidget()
        self.power_classes_listbox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.power_classes_listbox.itemClicked.connect(self.power_classes_list_selected)
        self.power_classes_listbox.itemActivated.connect(self.power_classes_list_selected)

        self.buy_power_button = QPushButton("💲 Buy Power")
        self.buy_power_button.setFixedSize(120,30)
        self.buy_power_button.setStyleSheet("font-size: 14px;")
        self.buy_power_button.setToolTip('-2CS Resources per Power')
        self.buy_power_button.setEnabled(False)
        self.remove_power_button = QPushButton("❌ Remove Power")
        self.remove_power_button.setFixedSize(130,30)
        self.remove_power_button.setStyleSheet("font-size: 14px;")
        self.remove_power_button.setEnabled(False)
        self.buy_power_button.clicked.connect(self.buy_power)
        self.remove_power_button.clicked.connect(self.remove_power)

        #create images
        self.villain_bubble_image = QLabel()
        self.villain_bubble_pixmap = QPixmap("")
        self.villain_bubble_image.setFixedSize(255,125)
        self.villain_image = QLabel()
        self.villain_pixmap = QPixmap("")
        self.villain_image.setFixedSize(350,200)
        
        self.roll_power_button = QPushButton("🎲 Roll Power\nv")
        self.roll_power_button.setFixedSize(170,60)
        self.roll_power_button.setEnabled(False)
        self.roll_power_button.clicked.connect(self.roll_power)
        power_label = QLabel("Power:")
        self.power_textbox = QLineEdit()
        bonus_powers_label = QLabel("Bonus Powers:")
        self.bonus_powers_listbox = QListWidget()
        optional_powers_label = QLabel("Optional Powers:")
        self.optional_powers_listbox = QListWidget()
        self.bonus_powers_listbox.setSelectionMode(QAbstractItemView.MultiSelection)
        self.optional_powers_listbox.setSelectionMode(QAbstractItemView.MultiSelection)
        
        self.add_power_button = QPushButton("➕ Add Power(s)\nv")
        self.add_power_button.setFixedSize(160,60)
        self.add_power_button.setEnabled(False)
        self.add_power_button.clicked.connect(self.add_power)
        powers_label = QLabel("Powers:")
        self.powers_listbox = QListWidget()
        self.powers_listbox.setFixedSize(450,254)
        self.powers_listbox.itemClicked.connect(self.powers_list_selected)
        self.powers_listbox.itemActivated.connect(self.powers_list_selected)
        self.num_powers_label = QLabel(" ")#leave blank until number of powers is rolled
        self.num_powers_label.setStyleSheet("font-size: 12px;")
        self.num_powers_label.setFixedSize(450,70)
        self.num_powers_label.setAlignment(Qt.AlignTop)
        self.generate_weakness_button = QPushButton("🎲 Generate Weakness")
        self.generate_weakness_button.setFixedSize(170,30)
        self.generate_weakness_button.setStyleSheet("font-size: 14px;")
        self.generate_weakness_button.setEnabled(False)
        self.generate_weakness_button.clicked.connect(self.generate_weakness)
        powers_weakness_label = QLabel("Weaknesses:")
        self.powers_weakness_textbox = QTextEdit()
        self.setupTextBox(self.powers_weakness_textbox, 450, 60, align=0)

        powers_tab_layout.addWidget(self.roll_power_classes_button, 0, 0, 
                                    alignment=Qt.AlignHCenter)
        powers_tab_layout.addWidget(power_classes_label, 1, 0)
        powers_tab_layout.addWidget(self.power_classes_listbox, 2, 0, 5, 1)
        buy_remove_powers_layout.addWidget(self.buy_power_button)
        buy_remove_powers_layout.addWidget(self.remove_power_button)

        powers_tab_layout.addWidget(self.roll_power_button, 0, 1, alignment=Qt.AlignHCenter)
        powers_tab_layout.addWidget(power_label, 1, 1)
        powers_tab_layout.addWidget(self.power_textbox, 2, 1)
        powers_tab_layout.addWidget(bonus_powers_label, 3, 1)
        powers_tab_layout.addWidget(self.bonus_powers_listbox, 4, 1)
        powers_tab_layout.addWidget(optional_powers_label, 5, 1)
        powers_tab_layout.addWidget(self.optional_powers_listbox, 6, 1)

        powers_tab_layout.addWidget(self.add_power_button, 0, 2, alignment=Qt.AlignTop)
        powers_tab_layout.addWidget(powers_label, 1, 2)
        powers_tab_layout.addWidget(self.powers_listbox, 2, 2, 6, 2, alignment=Qt.AlignTop)
        powers_tab_layout.addWidget(self.num_powers_label, 7, 2, alignment=Qt.AlignTop)
        powers_tab_layout.addWidget(self.generate_weakness_button, 8, 2, alignment=Qt.AlignBottom)
        powers_tab_layout.addWidget(powers_weakness_label, 9, 2)
        powers_tab_layout.addWidget(self.powers_weakness_textbox, 10, 2)

        powers_tab_layout.addLayout(buy_remove_powers_layout, 7, 0, alignment=Qt.AlignTop)
        powers_tab_layout.addWidget(self.villain_bubble_image, 8, 0, 3, 1)
        powers_tab_layout.addWidget(self.villain_image, 7, 1, 4, 1)
        
        #apply the main layout to the tab
        self.powers_tab.setLayout(powers_tab_layout)

        

    def setup_talents_tab(self):
        talents_tab_layout = QGridLayout()
        buy_remove_talents_layout = QHBoxLayout()

        #left column
        self.roll_talent_classes_button = QPushButton("🎲 Roll Talent Classes\nv")
        self.roll_talent_classes_button.setFixedSize(200,60)
        self.roll_talent_classes_button.setEnabled(False)
        self.roll_talent_classes_button.clicked.connect(self.roll_talent_classes)
        talent_classes_label = QLabel("Talent Classes:")
        self.talent_classes_listbox = QListWidget()
        self.talent_classes_listbox.setFixedSize(325,200)
        self.buy_talent_button = QPushButton("💲 Buy Talent")
        self.buy_talent_button.setFixedSize(120,30)
        self.buy_talent_button.setStyleSheet("font-size: 14px;")
        self.buy_talent_button.setEnabled(False)
        self.buy_talent_button.setToolTip('-1CS Resources per Talent')
        self.remove_talent_button = QPushButton("❌ Remove Talent")
        self.remove_talent_button.setFixedSize(130,30)
        self.remove_talent_button.setStyleSheet("font-size: 14px;")
        self.remove_talent_button.setEnabled(False)
        self.talent_classes_listbox.itemClicked.connect(self.talent_classes_list_selected)
        self.talent_classes_listbox.itemActivated.connect(self.talent_classes_list_selected)
        self.buy_talent_button.clicked.connect(self.buy_talent)
        self.remove_talent_button.clicked.connect(self.remove_talent)

        #middle column
        self.roll_talent_button = QPushButton("🎲 Roll Talent\nv")
        self.roll_talent_button.setFixedSize(170,60)
        self.roll_talent_button.setEnabled(False)
        self.roll_talent_button.clicked.connect(self.roll_talent)
        select_talent_label = QLabel("Select Talent:")
        self.select_talent_listbox = QListWidget()
        self.select_talent_listbox.setFixedSize(325,130)
        self.select_talent_listbox.itemClicked.connect(self.select_talent_selected)
        self.select_talent_listbox.itemActivated.connect(self.select_talent_selected)
        
        #right column
        talents_label = QLabel("Talents:")
        self.talents_listbox = QListWidget()
        self.talents_listbox.setFixedSize(375,300)
        self.num_talents_label = QLabel(" ")#leave blank until number of talents are rolled
        self.num_talents_label.setStyleSheet("font-size: 12px;")
        self.num_talents_label.setAlignment(Qt.AlignTop)
        self.num_talents_label.setFixedSize(375,20)
        self.talents_listbox.itemClicked.connect(self.talent_list_selected)
        self.talents_listbox.itemActivated.connect(self.talent_list_selected)

        #create the images
        self.talent_image = QLabel()
        self.talent_pixmap = QPixmap("")
        self.talent_image.setPixmap(self.talent_pixmap)
        self.talent_image.setFixedSize(325,222)
        self.talent2_image = QLabel()
        self.talent2_pixmap = QPixmap("")
        self.talent2_image.setPixmap(self.talent2_pixmap)
        self.talent2_image.setFixedSize(325,330)
        self.talent3_image = QLabel()
        self.talent3_pixmap = QPixmap("")
        self.talent3_image.setPixmap(self.talent3_pixmap)
        self.talent3_image.setFixedSize(375,130)

        talents_tab_layout.addWidget(self.roll_talent_classes_button, 0, 0, 
                                     alignment=Qt.AlignHCenter)
        talents_tab_layout.addWidget(talent_classes_label, 1, 0, alignment=Qt.AlignTop)
        talents_tab_layout.addWidget(self.talent_classes_listbox, 2, 0, 3, 1, alignment=Qt.AlignTop)
        buy_remove_talents_layout.addWidget(self.buy_talent_button)
        buy_remove_talents_layout.addWidget(self.remove_talent_button)

        talents_tab_layout.addWidget(self.roll_talent_button, 0, 1, 
                                     alignment=Qt.AlignHCenter)
        talents_tab_layout.addWidget(select_talent_label, 1, 1, alignment=Qt.AlignTop)
        talents_tab_layout.addWidget(self.select_talent_listbox, 2, 1, 2, 1, alignment=Qt.AlignTop)

        talents_tab_layout.addWidget(talents_label, 1, 2, alignment=Qt.AlignTop)
        talents_tab_layout.addWidget(self.talents_listbox, 2, 2, 5, 1, alignment=Qt.AlignTop)
        talents_tab_layout.addWidget(self.num_talents_label, 7, 2, alignment=Qt.AlignTop)

        talents_tab_layout.addLayout(buy_remove_talents_layout, 5, 0)
        talents_tab_layout.addWidget(self.talent_image, 6, 0, 3, 1)
        talents_tab_layout.addWidget(self.talent2_image, 4, 1, 5, 1)
        talents_tab_layout.addWidget(self.talent3_image, 8, 2, alignment=Qt.AlignTop)

        #apply the main layout to the tab
        self.talents_tab.setLayout(talents_tab_layout)



    def setup_contacts_tab(self):
        contacts_tab_layout = QGridLayout()

        #Left column
        contact_classes_label = QLabel("Contact Classes:")
        self.contacts_classes_listbox = QListWidget()
        self.contacts_classes_listbox.setFixedSize(325,150)
        self.buy_contact_button = QPushButton("💲 Buy Contact")
        self.buy_contact_button.setFixedSize(120,30)
        self.buy_contact_button.setStyleSheet("font-size: 14px;")
        self.buy_contact_button.setEnabled(False)
        self.buy_contact_button.setToolTip('-1CS Resources per Contact')
        self.buy_contact_button.clicked.connect(self.buy_contact)
        self.contacts_classes_listbox.itemClicked.connect(self.contact_class_list_selected)
        self.contacts_classes_listbox.itemActivated.connect(self.contact_class_list_selected)

        #Middle column
        self.roll_contact_classes_button = QPushButton("🎲 Roll Contacts\nv")
        self.roll_contact_classes_button.setFixedSize(150,60)
        self.roll_contact_classes_button.setEnabled(False)
        self.roll_contact_classes_button.clicked.connect(self.roll_contact_classes)
        select_contact_label = QLabel("Select Contact:")
        self.select_contact_listbox = QListWidget()
        self.select_contact_listbox.setFixedSize(325,424)
        self.select_contact_listbox.itemClicked.connect(self.select_contact_list_selected)
        self.select_contact_listbox.itemActivated.connect(self.select_contact_list_selected)

        #Right column
        contacts_label = QLabel("Contacts:")
        self.contacts_listbox = QListWidget()
        self.num_contacts_label = QLabel(" ")#leave blank until number of talents are rolled
        self.num_contacts_label.setStyleSheet("font-size: 12px;")
        self.contacts_listbox.itemClicked.connect(self.contact_list_selected)
        self.contacts_listbox.itemActivated.connect(self.contact_list_selected)

        #create the images
        self.contact_image = QLabel()
        self.contact_pixmap = QPixmap("")
        self.contact_image.setPixmap(self.contact_pixmap)
        self.contact_image.setFixedSize(325,285)
        self.contact2_image = QLabel()
        self.contact2_pixmap = QPixmap("")
        self.contact2_image.setPixmap(self.contact2_pixmap)
        self.contact2_image.setFixedSize(390,285)

        contacts_tab_layout.addWidget(contact_classes_label, 1, 0)
        contacts_tab_layout.addWidget(self.contacts_classes_listbox, 2, 0, 2, 1, alignment=Qt.AlignTop)
        contacts_tab_layout.addWidget(self.buy_contact_button, 4, 0, alignment=Qt.AlignTop)
        contacts_tab_layout.addWidget(self.contact_image, 5, 0)

        contacts_tab_layout.addWidget(self.roll_contact_classes_button, 0, 1, 
                                     alignment=Qt.AlignHCenter)
        contacts_tab_layout.addWidget(select_contact_label, 1, 1)
        contacts_tab_layout.addWidget(self.select_contact_listbox, 2, 1, 4, 1, alignment=Qt.AlignTop)

        contacts_tab_layout.addWidget(contacts_label, 1, 2)
        contacts_tab_layout.addWidget(self.contacts_listbox, 2, 2, 2, 1)
        contacts_tab_layout.addWidget(self.num_contacts_label, 4, 2, alignment=Qt.AlignTop)
        contacts_tab_layout.addWidget(self.contact2_image, 5, 2)

        #apply the main layout to the tab
        self.contacts_tab.setLayout(contacts_tab_layout)



    def setupTextBox(self, textbox, x, y, align):
        textbox.setReadOnly(True)
        textbox.setFixedSize(x, y)
        if align:
            textbox.setAlignment(Qt.AlignCenter)



################### USER INTERACTION FUNTIONS ###################
    #click the Physical Form Random button
    def physical_form_random(self):
        formindex = self.physical_form_roll()
        self.physical_form_list.setCurrentRow(formindex)
        #continue to physical_form_list_selected to fill in the other textboxes
        item = self.physical_form_list.currentItem()
        self.physical_form_list_selected(item)


    def physical_form_roll(self):
        roll = randint(1, 100)
        #map roll ranged to indices in the physical form list
        #roll_ranges = [(roll, index),...]
        roll_ranges = [
            (27, 0), (31, 1), (34, 2), (36, 3), (39, 4), (47, 5), (50, 7),
            (52, 8), (54, 9), (58, 10), (59, 11), (60, 12), (61, 13), (63, 14),
            (65, 15), (67, 16), (68, 17), (69, 18), (70, 19), (73, 21), (75, 22),
            (77, 23), (80, 24), (83, 25), (85, 26), (86, 27), (87, 28), (88, 29),
            (89, 30), (90, 31), (91, 32), (92, 33), (93, 34), (94, 35), (95, 36),
            (96, 37), (97, 38), (98, 39), (99, 40), (100, 41), (101, 42)
        ]
        for threshold, index in roll_ranges:
            if roll < threshold:
                return index



    #click the Physical Form List or continue from using the Random button
    def physical_form_list_selected(self, item):
        #reset the text boxes each time an item is selected in the physical form list
        self.options_list.clear()
        self.compound_list.clear()
        self.bonuses_textbox.clear()
        self.penalties_textbox.clear()
        self.weakness_textbox.clear()
        self.notes_textbox.clear()
        self.options_list.setEnabled(True)
        self.compound_list.setEnabled(True)
        self.physicalforms["Compound"] = 0
        #clear bonus attributes
        self.clear_info()
        #clear attribute tab boxes; disable bonus buttons
        self.table_text_box.clear()
        for ability, inputs in self.ability_inputs.items():
            inputs["roll"].clear()
            inputs["rank_roll"].clear()
            inputs["bonus"].clear()
            inputs["rank"].clear()
            inputs["score"].clear()
        for ability in self.ability_inputs:
            bonus_button = self.ability_inputs[ability]["bonus_button"]
            bonus_button.setEnabled(False)
        self.health_textbox.clear()
        self.karma_textbox.clear()
        for ability, inputs in self.secondary_ability_inputs.items():
            inputs["roll"].clear()
            inputs["rank_roll"].clear()
            inputs["bonus"].clear()
            inputs["rank"].clear()
            inputs["score"].clear()
        self.roll_power_classes_button.setEnabled(False)
        self.power_classes_listbox.clear()
        self.buy_power_button.setEnabled(False)
        self.remove_power_button.setEnabled(False)
        self.num_powers_label.setText("")
        self.roll_power_button.setEnabled(False)
        self.power_textbox.clear()
        self.add_power_button.setEnabled(False)
        self.bonus_powers_listbox.clear()
        self.optional_powers_listbox.clear()
        self.powers_listbox.clear()
        self.powers_listbox.setEnabled(True)
        self.powers_weakness_textbox.clear()
        self.generate_weakness_button.setEnabled(False)
        self.roll_talent_classes_button.setEnabled(False)
        self.talent_classes_listbox.clear()
        self.buy_talent_button.setEnabled(False)
        self.remove_talent_button.setEnabled(False)
        self.talents_listbox.clear()
        self.talents_listbox.setEnabled(True)
        self.contacts_classes_listbox.clear()
        self.contacts_classes_listbox.setEnabled(True)
        self.roll_contact_classes_button.setEnabled(False)
        self.select_contact_listbox.clear()
        self.contacts_listbox.clear()
        self.buy_contact_button.setEnabled(False)
        self.num_powers_label.setText("")
        self.num_talents_label.setText("")
        self.num_contacts_label.setText("")


        #origin of power
        originRoll = randint(1,100)
        if originRoll < 11:
            self.origin_textbox.setText("Natal")
        elif originRoll < 21:
            self.origin_textbox.setText("Maturity")
        elif originRoll < 31:
            self.origin_textbox.setText("Self-Achievement")
        elif originRoll < 36:
            self.origin_textbox.setText("Endowment")
        elif originRoll < 51:
            self.origin_textbox.setText("Technical Mishap")
        elif originRoll < 61:
            self.origin_textbox.setText("Technical Procedure")
        elif originRoll < 66:
            self.origin_textbox.setText("Creation")
        elif originRoll < 77:
            self.origin_textbox.setText("Biological Exposure")
        elif originRoll < 88:
            self.origin_textbox.setText("Chemical Exposure")
        elif originRoll < 99:
            self.origin_textbox.setText("Energy Exposure")
        else:
            self.origin_textbox.setText("Rebirth")

        self.physical_form_info(item, chance=100)



    def physical_form_info(self, item, chance):
        # Get the parent QListWidget of the selected item
        # to get the index of the selected item
        index = item.listWidget().row(item)

        bonus1 = {
            0: {"text": "Normal Humans get +1CS Resources; ", "effects": {"resources_bonus": 1}},
            1: {"text": "Induced Mutants can raise any one Primary Ability +1CS; ", "effects": {"ability_bonus": 1}},
            2: {"text": "Endurance is raised +1CS; ", "effects": {"endurance_bonus": 1}},
            3: {"text": "Endurance is raised +1CS; ", "effects": {"endurance_bonus": 1}},
            4: {"text": "Androids may raise any one Ability +1CS; ", "effects": {"ability_bonus": 1}},
            5: {"text": "Can raise any one Ability +1CS; ", "effects": {"ability_bonus": 1}},
            6: {"text": "Strength, Fighting, and Endurance are all increased +1CS; ", "effects": {"fighting_bonus": 1, "strength_bonus": 1, "endurance_bonus": 1}},
            8: {"text": "Musculars gain +1CS Strength and Endurance; ", "effects": {"strength_bonus": 1, "endurance_bonus": 1}},
            11: {"text": "Demihuman-Centaurs get +1 Strength; ", "effects": {"strength_bonus": 1}},
            19: {"text": "Merhumans gain +1CS Popularity; ", "effects": {"popularity_bonus": 1}},
            28: {"text": "+2CS Reason; ", "effects": {"reason_bonus": 2}},
            29: {"text": "All Physical Abilities (FASE) are raised +1CS; ", "effects": {"fighting_bonus": 1, "agility_bonus": 1, "strength_bonus": 1, "endurance_bonus": 1}},
            30: {"text": "All primary abilities (FASERIP) are raised +2CS; ", "effects": {"fighting_bonus": 2, "agility_bonus": 2, "strength_bonus": 2, "endurance_bonus": 2, "reason_bonus": 2, "intuition_bonus": 2, "psyche_bonus": 2}},
            32: {"text": "Plants gain +2CS Endurance; ", "effects": {"endurance_bonus": 2}},
            33: {"text": "Endurance is raised +1CS; ", "effects": {"endurance_bonus": 1}},
            34: {"text": "Initial Health is doubled; ", "effects": {"health_multiplier": 1}},
            38: {"text": "Physical attacks have a decreased effect on Ethereals (-9CS); ", "effects": {}},
            39: {"text": "Strength and Endurance are increased by +1CS; ", "effects": {"strength_bonus": 1, "endurance_bonus": 1}},
            42: {"text": "A Collective Mass gains +2CS Resistance to physical or directed energy attacks (lasers, for example); ", "effects": {}},
        }

        bonus2 = {
            2: {"text": "Random Mutants gain +1 Power; ", "effects": {"power_bonus": 1}},
            3: {"text": "Intuition is raised +1CS; ", "effects": {"intuition_bonus": 1}},
            4: {"text": "Androids gain +1 Power; ", "effects": {"power_bonus": 1}},
            28: {"text": "+1CS Resources; ", "effects": {"resources_bonus": 1}},
            30: {"text": "+2 Powers; ", "effects": {"power_bonus": 2}},
        }

        penalty1 = {
            2: {"text": "Random Mutants start with -1CS Resources; ", "effects": {"resources_bonus": -1}},
            4: {"text": "Popularity is initially lowered -1CS; ", "effects": {"popularity_bonus": -1}},
            5: {"text": "Starting Resources are set at Poor; ", "effects": {"pf_resources_rank": 2}},
            6: {"text": "Starting Resources are set at Poor; ", "effects": {"pf_resources_rank": 2}},
            7: {"text": "All Modified Humans gain -1 Power initially; ", "effects": {"power_bonus": -1}},
            8: {"text": "All Modified Humans gain -1 Power initially; ", "effects": {"power_bonus": -1}},
            9: {"text": "All Modified Humans gain -1 Power initially; ", "effects": {"power_bonus": -1}},
            10: {"text": "All Modified Humans gain -1 Power initially; ", "effects": {"power_bonus": -1}},
            11: {"text": "Centaurs have Feeble Climbing ability; ", "effects": {}},
            13: {"text": "Popularity set to 0; gains Popularity more slowly than other Demihumans; ", "effects": {"pf_popularity_rank": 0}},
            15: {"text": "-1CS Popularity; ", "effects": {"popularity_bonus": -1}},
            17: {"text": "Initial Popularity is Feeble; ", "effects": {"pf_popularity_rank": 1}},
            18: {"text": "Initial Popularity is 0; ", "effects": {"pf_popularity_rank": 0}},
            21: {"text": "-1CS Intuition; ", "effects": {"intuition_bonus": -1}},
            23: {"text": "-1CS Intuition and Psyche; ", "effects": {"intuition_bonus": -1, "psyche_bonus": -1}},
            24: {"text": "Augmenteds receive -1 Power; ", "effects": {"power_bonus": -1}},
            25: {"text": "Popularity set to 0; ", "effects": {"pf_popularity_rank": 0}},
            28: {"text": "Fighting is decreased -1CS; ", "effects": {"fighting_bonus": -1}},
            30: {"text": "0 Popularity with the hierarchy of the major established Earth religions; ", "effects": {}},
            31: {"text": "Animals have -1 Power; ", "effects": {"power_bonus": -1}},
            32: {"text": "Plants have -2CS Fighting; ", "effects": {"fighting_bonus": -2}},
            34: {"text": "Movement rate is decreased -1CS; ", "effects": {}},
            35: {"text": "Gas Bodies have 0 Resources and no initial Contacts; ", "effects": {"pf_resources_rank": 0, "initial_contacts": 0}},
            38: {"text": "Fighting rank is zero in the Earth Dimension, unless the Ethereal is fighting another Ethereal; ", "effects": {}},
            40: {"text": "-1CS Popularity; ", "effects": {"popularity_bonus": -1}},
        }

        notes1 = {
            3: {"text": "Breed Mutants must have at least one Contact, usually their tribe; ", "effects": {"initial_contacts": 2, "contact": "Breed Mutant's tribe"}},
            4: {"text": "Androids have at least one Contact, the lab tech or scientist who created them; ", "effects": {"initial_contacts": 2, "contact": "Android's creator"}},
            5: {"text": "A Humanoid starts out with only one Contact, his race; ", "effects": {"initial_contacts": 1, "contact": "Humanoid's race"}},
            6: {"text": "Composites heal twice as quickly as Normal Humans; ", "effects": {}},
            7: {"text": "Organics heal twice as fast as Normal Humans; ", "effects": {}},
            9: {"text": "Skeletals gain +1CS Resistance to Physical Attacks; ", "effects": {}},
            11: {"text": "Can move quickly over horizontal ground (4 areas/turn), and can fight with their hooves; ", "effects": {}},
            12: {"text": "Kicking does +1CS damage; ", "effects": {}},
            13: {"text": "Feeble Mental Domination over females of any human(oid) race; ", "effects": {}},
            14: {"text": "A felinoid can see in the dark with Excellent night vision; ", "effects": {}},
            15: {"text": "A lupinoid possesses an Excellent sense of smell; ", "effects": {}},
            17: {"text": "Chiropterans possess the Power of Active Sonar at Good rank; ", "effects": {}},
            18: {"text": "Venomous (Excellent Intensity poison); ", "effects": {}},
            19: {"text": "Merhumans possess both lungs and gills, but can only stay away from water a limited time because their bodies quickly dry out. Movement on dry land is limited to crawling or dependence on vehicles. Merhumans also possess Water Freedom; ", "effects": {}},
            20: {"text": "A player can combine any animal with a human to create a new Demihuman, then work with the Judge to provide it with reasonable statistics; ", "effects": {}},
            21: {"text": "At least one Contact must be either the lab or hospital that created him or a facility that provides maintenance services; ", "effects": {"initial_contacts": 2, "contact": "Lab or hospital responsible for creating or maintaining the cyborg"}},
            23: {"text": "Monstrous Resistance to Disease and Poisons of all sorts; ", "effects": {}},
            25: {"text": "The average Human Shape Robot weighs 500 to 2,000 pounds; ", "effects": {}},
            27: {"text": "Generate separate Physical abilities for each form and assign Powers to either or multiple forms. Metamorphs have a minimum of two forms. -1CS to all Primary Abilities for each additional form; ", "effects": {}},
            28: {"text": "Assume that all sentient computers have a minimum of one remotely controlled industrial robot. The owners think this robot is only used for self-maintenance and experimentation; Loss of all electrical power to the mainframe causes deactivation and loss of some of the computer's abilities and all of its Karma. Abilities and Powers are reduced -1CS across the board; ", "effects": {}},
            29: {"text": "Angels and demons have no initial Contacts but will soon be sought out by groups who see them as symbols or tools; ", "effects": {"initial_contacts": 0}},
            30: {"text": "Deities cannot really die in the Earth Dimension unless the slayer is another deity. Each deity has a home dimension; on that plane the deity loses his special protection from death; ", "effects": {}},
            31: {"text": "Animals automatically have two Detection Powers at Good rank; ", "effects": {"animal_detection": 1}},
            32: {"text": "Plants have 0 Resources; ", "effects": {"pf_resources_rank": 0}},
            34: {"text": "Mineral Life is immune to all Poisons and Diseases that harm Normal Humans; ", "effects": {}},
            35: {"text": "Gas Bodies possess a natural form of Phasing that permits them to penetrate solids; ", "effects": {}},
            36: {"text": "If the liquid life possesses Endurance and Psyche ranks of Excellent or better, the Fluid Body can form an erect simulation of a human body; ", "effects": {}},
            37: {"text": "Energy Beings have a Bonus Power of Energy Emission. Energy Control is an Optional Power; ", "effects": {"energy_form": 1}},
            38: {"text": "The visibility of an Ethereal varies according to their whim; They can be invisible, transparent, translucent, or opaque; ", "effects": {}},
            39: {"text": "Special means are required to maintain the reunion of mind and body. This can be anything from being frequently re-embalmed to utilizing any of the Vampiric Powers. If the Undead fails to follow his required - maintenance procedures, he begins to fall apart. In Undead terms, this is what Health points are used for. Health is the structural integrity of the Undead's own corpse.; ", "effects": {}},
            40: {"text": "Click each Compound form to determine which Table to use to roll Abilities and which Bonuses, Penalties, etc. are part of the Compound Form; ", "effects": {}},
            41: {"text": "Rolled Abilities are the base rank and score. Any Bonuses, Penalties, etc. only apply when the Changeling is in that form; Powers can be assigned to any or all Aspects. Each Aspect must have a unique Power not shared with other Aspects; ", "effects": {}},
            42: {"text": "Because of its peculiar dual nature, a Collective Mass has two sets of primary abilities. The first set represents the average abilities possessed by the individual component entities; the second set is that of the Collective Mass. The majority of powers can only be manifested by the Collective Mass. Individual entities can at best exhibit Feeble-rank versions of the available powers; Ordinarily, the number of individuals composing the Collective Mass is less than the rank number of the Collective Mass's Reason, multiplied by 100; ", "effects": {}},
        }

        notes2 = {
            6: {"text": "The Composite initially possesses one Contact - the hospital or person responsible for their creation; ", "effects": {"initial_contacts": 1, "contact": "hospital/person responsible for the character's creation"}},
            7: {"text": "At least one Contact should be the organization responsible for the modification; ", "effects": {"initial_contacts": 2, "contact": "organization responsible for the modification of the character"}},
            8: {"text": "At least one Contact should be the organization responsible for the modification; ", "effects": {"initial_contacts": 2, "contact": "organization responsible for the modification of the character"}},
            9: {"text": "At least one Contact should be the organization responsible for the modification; ", "effects": {"initial_contacts": 2, "contact": "organization responsible for the modification of the character"}},
            10: {"text": "At least one Contact should be the organization responsible for the modification; ", "effects": {"initial_contacts": 2, "contact": "organization responsible for the modification of the character"}},
            14: {"text": "A felinoid possesses +1CS Climbing ability; ", "effects": {}},
            18: {"text": "Lamians are difficult to bind (+1CS to escape); ", "effects": {}},
            23: {"text": "Mech Bodies initially have only one Contact—the lab where they were created; ", "effects": {"initial_contacts": 1, "contact": "lab where character was created"}},
            30: {"text": "Deities eventually attract any remaining living worshippers they still have. All of these people serve as Contacts; ", "effects": {}},
            31: {"text": "Animals have to have a human Contact; ", "effects": {"initial_contacts": 2, "contact": "Human contact"}},
            32: {"text": "Plants automatically possess Absorption Power of Good rank in the form of enhanced photosynthesis; ", "effects": {}},
            35: {"text": "The Gas Body is a coherent cloud that retains its integrity even in the face of Amazing Intensity winds; ", "effects": {}},
            36: {"text": "Fluid Bodies have a natural variation of Phasing that permits them to permeate any porous material; ", "effects": {}},
            37: {"text": "Physical contact with an Energy Being does Feeble damage; The Energy Body possesses an Intensity rank of its own; this is how the Health points apply to this being; ", "effects": {}},
            38: {"text": "While Ethereals are intangible on the Earth Dimension, they regain solidity in other Dimensions. In such realms Ethereals are vulnerable to all Powers except those that specifically affect Ethereals and other disembodied beings; these Powers are Spirit Summoning and Storage, Reincarnation, and Exorcism; ", "effects": {}}
        }

        notes3 = {
            30: {"text": "Deities automatically possess at least one Travel Power; ", "effects": {"deity_travel_power": 1}},
            31: {"text": "Resources are zero unless the animal has attached himself to a human. In this case, the Resource rank is assigned to that human; ", "effects": {}},
            32: {"text": "Plants have no initial Contacts; the exception is if the Plant was created by scientific means, in which case its creator might be a Contact; ", "effects": {}},
            35: {"text": "The only way to destroy a Gas Body is to alter its composition through Powers like Matter Conversion and Matter Control; ", "effects": {}},
            36: {"text": "Fluid Bodies have no initial Contacts except their own race, if one exists; ", "effects": {}},
            37: {"text": "The only way to destroy an Energy Body is to completely Negate or solidify its energy; ", "effects": {}}
        }

        weakness1 = {
            6: {"text": "Resistance to Mental Domination is reduced -1CS; ", "effects": {}},
            23: {"text": "Prone to things that never harm a flesh-bound character, like Magnetic attacks and rust; ", "effects": {}},
            28: {"text": "Computers have a decreased Resistance to Electrical and Magnetic Attacks and also to Phasing; ", "effects": {}},
            29: {"text": "Such beings possess a Psychological Weakness that Negates their Power; ", "effects": {}},
            32: {"text": "Prolonged deprivation of light and water reduces the hero's Strength and Endurance -1CS per day after an initial three days; ", "effects": {}},
            34: {"text": "Mineral Life is vulnerable to attacks with special effects on the body materials. For example, an iron golem is prone to rust; ", "effects": {}},
            35: {"text": "Cannot freely move in a vacuum unless it possesses a Travel or Energy Power; ", "effects": {}},
            36: {"text": "If the Fluid Body is frozen, the character is immobilized until they can melt. Vaporization is a fatal act for most Fluid Bodies; ", "effects": {}},
            37: {"text": "Energy Bodies possess a special vulnerability to Plasma Control (-1CS Resistance); ", "effects": {}},
            38: {"text": "Spirit Vampirism completely destroys Ethereals. Psi-Vampirism destroys the self-image and reduces the Ethereal to a mindless Poltergeist; ", "effects": {}},
            39: {"text": "Undead possess a Psychological Weakness; their Power is negated within 10' of a religious symbol. If the symbol is that of a religion the Undead practiced while alive, they suffer Excellent damage; ", "effects": {}},
            42: {"text": "A successful Grappling attack breaks the body into two masses. The body can automatically rejoin in 1-4 turns unless something prevents this; ", "effects": {}}
        }

        # Apply bonuses
        if index in bonus1 and randint(1, 100) <= chance:
            bonus = bonus1[index]
            self.bonuses_textbox.insertPlainText(bonus["text"])
            for attr, value in bonus["effects"].items():
                setattr(self, attr, getattr(self, attr) + value)

        if index in bonus2 and randint(1, 100) <= chance:
            bonus = bonus2[index]
            self.bonuses_textbox.insertPlainText(bonus["text"])
            for attr, value in bonus["effects"].items():
                setattr(self, attr, getattr(self, attr) + value)

        # Apply penalties
        if index in penalty1 and randint(1, 100) <= chance:
            penalty = penalty1[index]
            self.penalties_textbox.insertPlainText(penalty["text"])
            for attr, value in penalty["effects"].items():
                setattr(self, attr, getattr(self, attr) + value)

        # Add notes
        if index in notes1 and randint(1, 100) <= chance:
            print(f"notes1, index:{index}")
            note = notes1[index]
            print(f"notes1, note:{note}")
            if index == 18:
                venomous = randint(0,1)
                if venomous:
                    self.notes_textbox.insertPlainText(note["text"])
            else:
                self.notes_textbox.insertPlainText(note["text"])
            if self.initial_contacts > 0:
                note = notes1[index]
                self.contacts_listbox.addItem(note["effects"]["contact"])
                contact_item = self.contacts_listbox.item(self.contacts_listbox.count() - 1)
                contact_item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        if index in notes2 and randint(1, 100) <= chance:
            note = notes2[index]
            self.notes_textbox.insertPlainText(note["text"])
            if self.initial_contacts > 0:
                self.contacts_listbox.addItem(note["effects"]["contact"])
                contact_item = self.contacts_listbox.item(self.contacts_listbox.count() - 1)
                contact_item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        if index in notes3 and randint(1, 100) <= chance:
            note = notes3[index]
            self.notes_textbox.insertPlainText(note["text"])
        if index in weakness1 and randint(1, 100) <= chance:
            weakness = weakness1[index]
            self.weakness_textbox.insertPlainText(weakness["text"])


        bonus3_chance = randint(1,100)
        print(f"Physical Form Info bonus3= {bonus3_chance}")
        if bonus3_chance <= chance:
            #Bonuses Pt3
            if index == 30: # Deity
                self.bonuses_textbox.insertPlainText("+2CS Popularity with the public; ")


        penalty2_chance = randint(1,100)
        print(f"Physical Form Info penalty2= {penalty2_chance}")
        if penalty2_chance <= chance:
            #Penalties Pt2
            if index == 6: # Surgical Composites
                self.penalties_textbox.insertPlainText("Popularity is set to 0; ")
                self.pf_popularity_rank = 0


        weakness2_chance = randint(1,100)
        print(f"Physical Form Info weakness2= {weakness2_chance}")
        if weakness2_chance <= chance:
            #Weaknesses Pt2
            if index == 37: # Energy
                self.weakness_textbox.insertPlainText("Energy Bodies can be contained"
                                                    " within special storage "
                                                    "batteries; this is the only "
                                                    "way to immobilize these beings; ")



        #Physical Form Options
        if index == 10: # Modified Human-Extra Parts
            self.options_list.addItem("Extra arms raise Fighting +1CS")
            self.options_list.addItem("Duplicate organs doubles Health")
            self.options_list.addItem("Tails give the hero +1 attack")
            self.options_list.addItem("Wings give the hero Flight")
            self.options_list.addItem("Extra legs give +1 area movement")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
        elif index == 16: # Demihuman-Avian
            self.options_list.addItem("Angelic")
            self.options_list.addItem("Harpy")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
        elif index == 24: # Cyborg-Mechanically Augmented
            self.options_list.addItem("Resources are Good")
            self.options_list.addItem("Resources are optionally rolled")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
        elif index == 27: # Robot-Metamorphic
            self.options_list.addItem("2 forms")
            self.options_list.addItem("3 forms")
            self.options_list.addItem("4 forms")
            self.options_list.addItem("5 forms")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
        elif index == 29: # Angel / Demon
            self.options_list.addItem("Angel")
            self.options_list.addItem("Demon")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
        elif index == 31: # Animal
            self.options_list.addItem("Terrestrial Animal")
            self.options_list.addItem("Extraterrestrial Animal")
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_options.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)

        #Changeling/Compound Form List
        if index == 40 or index == 41: # Compound and Changeling
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_compound.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
            num = self.number_of_compoundforms()
            self.compound_forms = num
            while num > 0:
                formindex = self.physical_form_roll()
                #do not allow Metamorphic Robots or Compound\Changelings to be 
                #part of a Compound Form as it seriously complicates things
                if formindex == 27 or formindex == 40 or formindex == 41:
                    continue
                item = self.physical_form_list.item(formindex)
                form = item.text()
                self.compound_list.addItem(form)
                num -= 1
        
        #enable Roll Abilities button if form does not require using the options
        #or compound lists; make sure button remains disabled until lists are used
        options = self.options_list.count()
        compound_forms = self.compound_list.count()
        if options == 0 and compound_forms == 0:
            self.abilities_button.setEnabled(True)
            self.abilities_button.setFocus()
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_abilities.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
            self.cap_pixmap = QPixmap(resource_path('images/capt_america.jpg'))
            self.cap_image.setPixmap(self.cap_pixmap)
            self.ironman_pixmap = QPixmap(resource_path('images/bubble_abilities.jpg'))
            self.ironman_image.setPixmap(self.ironman_pixmap)
        else:
            self.abilities_button.setEnabled(False)
            self.cap_pixmap = QPixmap("")
            self.cap_image.setPixmap(self.cap_pixmap)
            self.ironman_pixmap = QPixmap("")
            self.ironman_image.setPixmap(self.ironman_pixmap)
        
        self.bubble_pixmap = QPixmap("")
        self.bubble_image.setPixmap(self.bubble_pixmap)
        self.blackpanther_pixmap = QPixmap("")
        self.blackpanther_image.setPixmap(self.blackpanther_pixmap)
        self.villain_bubble_pixmap = QPixmap("")
        self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
        self.villain_pixmap = QPixmap("")
        self.villain_image.setPixmap(self.villain_pixmap)
        self.talent_pixmap = QPixmap("")
        self.talent_image.setPixmap(self.talent_pixmap)
        self.talent2_pixmap = QPixmap("")
        self.talent2_image.setPixmap(self.talent2_pixmap)
        self.contact_pixmap = QPixmap("")
        self.contact_image.setPixmap(self.contact_pixmap)
        self.contact2_pixmap = QPixmap("")
        self.contact2_image.setPixmap(self.contact2_pixmap)
        


    #determine the number of compound/changeling forms
    def number_of_compoundforms(self):
        roll = randint(1,100)
        if roll < 51:
            return 2
        elif roll < 76:
            return 3
        elif roll < 96:
            return 4
        else:
            return 5
        

    #Clicking or hitting Enter on an item in the Optional Forms List
    def options_list_selected(self, item):
        #convert the selected item to the selected string in the list box
        selected_text = item.text()
        # Get the parent QListWidget of the selected item
        list_widget = item.listWidget()
        # to get the index of the selected item in the Options list
        index = list_widget.row(item)
        # to get the index of the selected item in the Physical Form list
        row = self.physical_form_list.currentRow()
        print("Physical Form Option List Clicked!")
        print(f"options_list_selected item= {item}")
        print(f"options_list_selected text= {selected_text}")
        print(f"options_list_selected index= {index}")
        print(f"options_list_selected physical form row= {row}")
        print(f"resource_rank={self.resources_rank}")

        chance = 100

        #If this is a Compound form get the form from the current compound form
        #instead of the current physical form
        if row == 40:
            #add the optional form to the compound_form_options_list at the same
            #index as the compound_form_list index so that it can be added 
            #correctly to the file when saved
            print(f"current_compound_form_index= {self.current_compound_form_index}")
            self.compound_form_options_list.insert(self.current_compound_form_index, selected_text)
            print(f"compound_form_options_list= {self.compound_form_options_list}")
            self.current_compound_form_index += 1
            #find the compound form's index in the Physical Form list
            current_compound = self.current_compound_form
            matched_physical_forms = self.physical_form_list.findItems(current_compound, Qt.MatchExactly)
            if matched_physical_forms:  # Ensure the item exists
                #find the row of the item in the Physical Form List
                option = self.physical_form_list.row(matched_physical_forms[0])

                num = self.compound_forms
                print(f"options_list_selected num= {num}")
                chance = 100 / num
                print(f"options_list_selected chance= {chance}")
                
                compound_table = self.physicalforms["Compound"]
                print(f"compound_table = {compound_table}")
                compound_num = self.compound_list.count()
                compound_option_chance = randint(1,100)
                print(f"options_list_selected compound_option_chance= {compound_option_chance}")
                if compound_table == 0:#if no compound form table has been chosen
                    if option == 16 and index == 0:
                        if compound_num == 0:#and this is the last compound form
                            table = self.physicalforms["Demihuman-Avian"]["Angelic"]
                            self.physicalforms["Compound"] = table
                        elif compound_option_chance <= chance:#else use the chance
                            table = self.physicalforms["Demihuman-Avian"]["Angelic"]
                            self.physicalforms["Compound"] = table
                    elif option == 16 and index == 1:
                        if compound_num == 0:
                            table = self.physicalforms["Demihuman-Avian"]["Harpy"]
                            self.physicalforms["Compound"] = table
                        elif compound_option_chance <= chance:
                            table = self.physicalforms["Demihuman-Avian"]["Harpy"]
                            self.physicalforms["Compound"] = table
                    elif option == 31 and index == 0:
                        if compound_num == 0:
                            table = self.physicalforms["Animal"]["Terrestrial"]
                            self.physicalforms["Compound"] = table
                            print(f"Terrestrial Animals roll on Table 1")
                        elif compound_option_chance <= chance:
                            table = self.physicalforms["Animal"]["Terrestrial"]
                            self.physicalforms["Compound"] = table
                            print(f"Terrestrial Animals roll on Table 1")
                    elif option == 31 and index == 1:
                        if compound_num == 0:
                            table = self.physicalforms["Animal"]["Extraterrestrial"]
                            self.physicalforms["Compound"] = table
                            print(f"Extraterrestrial Animals roll on Table 5")
                        elif compound_option_chance <= chance:
                            table = self.physicalforms["Animal"]["Extraterrestrial"]
                            self.physicalforms["Compound"] = table
                            print(f"Extraterrestrial Animals roll on Table 5")

            new_compound_table = self.physicalforms["Compound"]
            print(f"new_compound_table = {new_compound_table}")
             

        print(f"options_list_selected chance= {chance}")
        if row == 10: #Modified Human-Extra Parts
            if index == 0:
                self.fighting_bonus += 1
                print(f"+1CS to Fighting")
            if index == 1:
                self.health_multiplier += 1
                print(f"Health x2")
            if index == 2:
                print(f"+1 attack")
            if index == 3:
                print(f"gain Flight")
                self.wings_travel_power = 1
            if index == 4:
                print(f"+1 area movement")
        elif row == 16: #Demihuman-Avian
            if index == 0:
                compound_option_chance1 = randint(1,100)
                print(f"options_list_selected compound_option_chance1= {compound_option_chance1}")
                if compound_option_chance1 <= chance:
                    self.bonuses_textbox.insertPlainText("Popularity +1CS; ")
                    self.popularity_bonus += 1
            if index == 1:
                compound_option_chance2 = randint(1,100)
                print(f"options_list_selected compound_option_chance2= {compound_option_chance2}")
                if compound_option_chance2 <= chance:
                    self.bonuses_textbox.insertPlainText("+1CS Fighting; ")
                    self.fighting_bonus += 1
                compound_option_chance3 = randint(1,100)
                print(f"options_list_selected compound_option_chance3= {compound_option_chance3}")
                if compound_option_chance3 <= chance:
                    self.notes_textbox.insertPlainText("Harpies possess arms that "
                                                    "are modified to also serve "
                                                    "as wings and feather-covered"
                                                    "legs that end in bird Claws; ")
        elif row == 24: #Cyborg-Mechanically Augmented
            if index == 0:
                self.pf_resources_rank = 4 #set resources to Good
            if index == 1:
                pass#Resources are optionally rolled
        elif row == 27: #Robot-Metamorphic (roll Abilities for each form)
            #apply penalty to abilities based on the number of forms above 2 (index 0)
            self.fighting_bonus -= index
            self.agility_bonus -= index
            self.strength_bonus -= index
            self.endurance_bonus -= index
            self.reason_bonus -= index
            self.intuition_bonus -= index
            self.psyche_bonus -= index
            #self.notes_textbox.insertPlainText(f"Robot-Metamorphic: {index+2} forms; ")
        elif row == 29: #Angel/Demon
            if index == 0:
                compound_option_chance4 = randint(1,100)
                print(f"options_list_selected compound_option_chance4= {compound_option_chance4}")
                if compound_option_chance4 <= chance:
                    self.bonuses_textbox.insertPlainText("Popularity +2CS; ")
                    self.popularity_bonus += 2
                compound_option_chance4b = randint(1,100)
                print(f"options_list_selected compound_option_chance4b= {compound_option_chance4b}")
                if compound_option_chance4b <= chance:
                    self.notes_textbox.insertPlainText("Angels automatically possess a specific "
                    "form of Artifact Creation that produces a magical sword that does Excellent damage.; ")
            if index == 1:
                compound_option_chance5 = randint(1,100)
                print(f"options_list_selected compound_option_chance5= {compound_option_chance5}")
                if compound_option_chance5 <= chance:
                    self.penalties_textbox.insertPlainText("Popularity -2CS; ")
                    self.popularity_bonus -= 2
                compound_option_chance5b = randint(1,100)
                print(f"options_list_selected compound_option_chance5= {compound_option_chance5b}")
                if compound_option_chance5b <= chance:
                    self.notes_textbox.insertPlainText("Demons automatically possess "
                    "Good Fire Generation and Specific Invulnerability to Heat and Fire; ")
        elif row == 31: #Animal
            if index == 0 :
                print(f"Terrestrial Animals roll on Table 1")
                table = self.physicalforms['Animal']["Terrestrial"]
            if index == 1:
                print(f"Extraterrestrial Animals roll on Table 5")
                table = self.physicalforms['Animal']["Extraterrestrial"]

        #if the form is a Compound then clear the list in case another form has options
        #the options are stored in the compound_form_options_list
        print(f"row={row}")
        if row == 40:
            print("row=40")
            #clear the list
            self.options_list.clear()
        else:
            print("row not 40")
            self.options_list.setEnabled(False)

        #if still choosing Compound forms enable the compound list to continue choosing
        self.compound_list.setEnabled(True)

        #enable Roll Abilities button unless this is a Compound form where 
        #all forms have not been selected
        compound_forms = self.compound_list.count()
        if compound_forms == 0:
            self.abilities_button.setEnabled(True)
            self.abilities_button.setFocus()
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_abilities.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)
            self.cap_pixmap = QPixmap(resource_path('images/capt_america.jpg'))
            self.cap_image.setPixmap(self.cap_pixmap)
            self.ironman_pixmap = QPixmap(resource_path('images/bubble_abilities.jpg'))
            self.ironman_image.setPixmap(self.ironman_pixmap)
        else:
            self.watcher_pixmap = QPixmap(resource_path('images/watcher_compound.jpg'))
            self.watcher_image.setPixmap(self.watcher_pixmap)


    #Clicking or hitting Enter on an item in the Compound Forms list
    def compound_list_selected(self, item):
        #convert the selected item to the selected string in the list box
        selected_text = item.text()
        # Get the parent QListWidget of the selected item
        list_widget = item.listWidget()
        # to get the index of the selected item
        index = list_widget.row(item)
        print("Compound Form List Clicked!")
        print(f"compound list item= {item}")
        print(f"compound list text= {selected_text}")
        print(f"compound list index= {index}")
        print(f"resource_rank={self.resources_rank}")

        self.current_compound_form = selected_text

        #Find the index of the form in the Physical Form list to use based on the
        #text of the item clicked in the Compound List and use it when filling in 
        #the bonuses and penalties boxes
        #First, create a list of items found matching the form clicked in 
        #Compound List with the form in the Physical Form List (should be just one item)
        matched_physical_forms = self.physical_form_list.findItems(selected_text, Qt.MatchExactly)
        if matched_physical_forms:  # Ensure the item exists
            #find the row of the item in the Physical Form List
            physicalformindex = self.physical_form_list.row(matched_physical_forms[0])
            item = matched_physical_forms[0]

        print(f"Compound Physical Form List index= {physicalformindex}")
        print(f"Compound Physical Form List item= {item}")
        #determine the chance the compound form takes of each bonus and penalty
        num = self.compound_forms
        chance = 100 / num
        print(f"number of forms = {num}")
        print(f"chance={chance}")
        #populate the info boxes by calculating the chance of each bonus and penalty
        self.physical_form_info(item, chance)


        #calculate which table to use
        #Demihuman Avian and Animal tables are determined by the optional list
        if selected_text != "Demihuman-Avian" and selected_text != "Animal":
            table_chance = randint(1,100)
            count = self.compound_list.count()
            compound_table = self.physicalforms["Compound"]
            table = self.physicalforms[selected_text]
            print(f"table chance = {table_chance}")
            print(f"count={count}")
            print(f"compound_table={compound_table}")
            print(f"table={table}")
            if compound_table == 0:#if no table has been chosen
                if count == 1:#if this is the last form use this table
                    self.physicalforms["Compound"] = table
                elif table_chance <= chance:#if not the last form calculate the chance
                    self.physicalforms["Compound"] = table
            
            new_compound_table = self.physicalforms["Compound"]
            print(f"new_compound_table = {new_compound_table}")

        #add the optional form to the compound_form_options_list at the same
        #index as the compound_form_list index so that it can be added 
        #correctly to the file when saved
        self.compound_form_list.insert(self.current_compound_form_index, selected_text)
        print(f"compound_form_list={self.compound_form_list}")

        #remove the item from the compound form list
        self.compound_list.takeItem(index)

        #enable Roll Abilities button unless this is a Compound form where 
        #all forms have not been selected
        options = self.options_list.count()
        options_selected = self.options_list.selectedItems()
        compound_forms = self.compound_list.count()
        if compound_forms == 0:#if all forms have been chosen
            if options > 0 and options_selected:#if options were available and selected
                self.abilities_button.setEnabled(True)
                self.abilities_button.setFocus()
                self.watcher_pixmap = QPixmap(resource_path('images/watcher_abilities.jpg'))
                self.watcher_image.setPixmap(self.watcher_pixmap)
                self.cap_pixmap = QPixmap(resource_path('images/capt_america.jpg'))
                self.cap_image.setPixmap(self.cap_pixmap)
                self.ironman_pixmap = QPixmap(resource_path('images/bubble_abilities.jpg'))
                self.ironman_image.setPixmap(self.ironman_pixmap)
            elif options == 0:#if no options are needed to be selected
                self.abilities_button.setEnabled(True)
                self.abilities_button.setFocus()
                self.watcher_pixmap = QPixmap(resource_path('images/watcher_abilities.jpg'))
                self.watcher_image.setPixmap(self.watcher_pixmap)
                self.cap_pixmap = QPixmap(resource_path('images/capt_america.jpg'))
                self.cap_image.setPixmap(self.cap_pixmap)
                self.ironman_pixmap = QPixmap(resource_path('images/bubble_abilities.jpg'))
                self.ironman_image.setPixmap(self.ironman_pixmap)

        #if options need to be selected disable the compound list to force the 
        #user to select an option before continuing choosing Compound forms
        #it will get re-enabled in the options_list_selection if there are still
        #forms to choose
        #increment the current_compound_form_index by one if no optional forms 
        #need to be selected and matched to the compound_form_list index
        if options and compound_forms:
            self.compound_list.setEnabled(False)
        if not options:
            self.current_compound_form_index += 1



    #Click the Roll Abilities button
    def roll_abilities(self):
        print("Roll Abilities Button Clicked!")
        #reset health and karma
        self.health = 0
        self.karma = 0
        #if physical form receives an ability bonus make sure to add one back if
        #one was used before re-rolling abilities
        if self.ability_bonus_button_was_clicked > 0:
            self.ability_bonus += 1
            self.ability_bonus_button_was_clicked = 0
        #Find the table to roll on
        item = self.physical_form_list.currentItem()
        selected_text = item.text()
        table = self.physicalforms[selected_text]
        print(f"roll abilities item={item}")
        print(f"roll abilities selected_text={selected_text}")
        print(f"roll abilities table={table}")
        if selected_text == "Demihuman-Avian":
            current_row = self.options_list.currentRow()
            print(current_row)
            if current_row == 0:
                table = self.physicalforms[selected_text]["Angelic"]
            else:
                table = self.physicalforms[selected_text]["Harpy"]
        if selected_text == "Animal":
            current_row = self.options_list.currentRow()
            print(current_row)
            if current_row == 0:
                table = self.physicalforms[selected_text]["Terrestrial"]
            else:
                table = self.physicalforms[selected_text]["Extraterrestrial"]
        
        print(f"roll abilities table={table}")
        
        #roll randomly for each ability then display the roll, rank and bonus
        #for each ability in the Table column
        self.fill_roll_textboxes(self.ability_inputs.items(), table)
        #enable the Bonus Buttons if the Physical Form requires it
        for ability, inputs in self.ability_inputs.items():
            if self.ability_bonus > 0:
                inputs["bonus_button"].setEnabled(True)

        #display Health and Karma after applying health multiplier
        self.health = self.health * self.health_multiplier
        self.health_textbox.setText(str(self.health))
        self.karma_textbox.setText(str(self.karma))

        #roll randomly for each secondary ability then display the roll, rank
        # and bonus for each ability in the Secondary column
        self.fill_roll_textboxes(self.secondary_ability_inputs.items(), table)

        if self.ability_bonus == 0:
            self.roll_power_classes_button.setEnabled(True)
            self.roll_power_classes_button.setFocus()
            self.bubble_pixmap = QPixmap(resource_path('images/bubble_blackpanther.jpg'))
            self.bubble_image.setPixmap(self.bubble_pixmap)
            self.blackpanther_pixmap = QPixmap(resource_path('images/black_panther.jpg'))
            self.blackpanther_image.setPixmap(self.blackpanther_pixmap)
            self.villain_bubble_pixmap = QPixmap(resource_path('images/drdoom_bubble.jpg'))
            self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
            self.villain_pixmap = QPixmap(resource_path('images/drdoom.jpg'))
            self.villain_image.setPixmap(self.villain_pixmap)
            self.cap_pixmap = QPixmap("")
            self.cap_image.setPixmap(self.cap_pixmap)
            self.ironman_pixmap = QPixmap("")
            self.ironman_image.setPixmap(self.ironman_pixmap)
        else:
            self.cap_pixmap = QPixmap("")
            self.cap_image.setPixmap(self.cap_pixmap)
            self.ironman_pixmap = QPixmap(resource_path('images/iron_man.jpg'))
            self.ironman_image.setPixmap(self.ironman_pixmap)
            self.bubble_pixmap = QPixmap("")
            self.bubble_image.setPixmap(self.bubble_pixmap)
            self.blackpanther_pixmap = QPixmap("")
            self.blackpanther_image.setPixmap(self.blackpanther_pixmap)
        
        self.watcher_pixmap = QPixmap("")
        self.watcher_image.setPixmap(self.watcher_pixmap)



    #Click one of the bonus ability rank buttons
    def bonus_ability_clicked(self, ability):
        print(f"Bonus button clicked for {ability}")
        #if the ability_bonus is still above 0
        if self.ability_bonus > 0:
            # Access the corresponding input fields using self.ability_inputs[ability]
            rank_textbox = self.ability_inputs[ability]["rank"]
            score_textbox = self.ability_inputs[ability]["score"]
            #get the current rank name for the ability
            current_rank_name = rank_textbox.text()
            current_rank_score = int(score_textbox.text())
            print(f"current_rank_name={current_rank_name}")
            print(f"current_rank_score={current_rank_score}")
            #get the index number from the ranks list
            index = self.ranks.index(current_rank_name)
            #add one to the ranks index
            index += 1
            #set the ability rank textbox to the new rank
            new_rank = self.ranks[index]
            print(f"new_rank={new_rank}")
            rank_textbox.setText(f"{new_rank}")

            #adjust rank score
            new_rank_score = self.min_std_rank_score(new_rank)
            score_textbox.setText(f"{new_rank_score}")

            #adjust Health/Karma
            diff = new_rank_score - current_rank_score
            if ability in {"fighting", "agility", "strength", "endurance"}:
                diff = diff * self.health_multiplier#apply health multiplier to the difference
                self.health += diff
                self.health_textbox.setText(f"{self.health}")
            elif ability in {"reason", "intuition", "psyche"}:
                self.karma += diff
                self.karma_textbox.setText(f"{self.karma}")

            self.ability_bonus -= 1 #reduce the number of ability bonuses by one
            #disable the buttons once all ability bonuses have been used
            if self.ability_bonus == 0:
                for ability in self.ability_inputs:
                    bonus_button = self.ability_inputs[ability]["bonus_button"]
                    bonus_button.setEnabled(False)
                self.roll_power_classes_button.setEnabled(True)
                self.roll_power_classes_button.setFocus()
                self.ironman_pixmap = QPixmap("")
                self.ironman_image.setPixmap(self.ironman_pixmap)

            self.ability_bonus_button_was_clicked += 1

        #display image to move user to the Powers tab    
        self.bubble_pixmap = QPixmap(resource_path('images/bubble_blackpanther.jpg'))
        self.bubble_image.setPixmap(self.bubble_pixmap)
        self.blackpanther_pixmap = QPixmap(resource_path('images/black_panther.jpg'))
        self.blackpanther_image.setPixmap(self.blackpanther_pixmap)
        self.villain_bubble_pixmap = QPixmap(resource_path('images/drdoom_bubble.jpg'))
        self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
        self.villain_pixmap = QPixmap(resource_path('images/drdoom.jpg'))
        self.villain_image.setPixmap(self.villain_pixmap)



    #Click the Roll Power Classes button
    def roll_power_classes(self):
        print("Rolling Power Classes...")
        print(f"resource_rank={self.resources_rank}")
        #disable the Abilities tab and reset the Powers tab
        self.abilities_button.setEnabled(False)
        self.power_classes_listbox.clear()
        self.roll_power_button.setEnabled(False)
        self.power_textbox.clear()
        self.add_power_button.setEnabled(False)
        self.bonus_powers_listbox.clear()
        self.optional_powers_listbox.clear()
        self.powers_listbox.clear()

        self.villain_bubble_pixmap = QPixmap(resource_path('images/mystique_bubble.jpg'))
        self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
        self.villain_pixmap = QPixmap(resource_path('images/mystique.jpg'))
        self.villain_image.setPixmap(self.villain_pixmap)
        self.bubble_pixmap = QPixmap("")
        self.bubble_image.setPixmap(self.bubble_pixmap)
        self.blackpanther_pixmap = QPixmap("")
        self.blackpanther_image.setPixmap(self.blackpanther_pixmap)

        if self.animal_detection == 1:
            #roll the two detection powers and apply power rank Good
                roll = randint(1,100)
                powers = list(powerlists.detection_powers_list.keys())
                roll_thresholds = [3, 5, 11, 15, 21, 29, 35, 41, 43, 45, 51, 55, 57,
                                    59, 60, 63, 70, 80, 91, 95, 99, 101]
                index = bisect(roll_thresholds, roll)
                power = powers[index]
                rank = self.ranks[4]
                score = self.min_std_rank_score(rank)
                self.powers_listbox.addItem(f"{power} - {rank} ({score})")
                item = self.powers_listbox.item(0)
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                # 2nd detection power
                roll = randint(1,100)
                index2 = bisect(roll_thresholds, roll)
                while index2 == index:#if the same power is rolled, roll again
                    roll = randint(1,100)
                    index2 = bisect(roll_thresholds, roll)
                power = powers[index2]
                score = self.min_std_rank_score(rank)
                self.powers_listbox.addItem(f"{power} - {rank} ({score})")
                item = self.powers_listbox.item(1)
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        
        item = self.physical_form_list.currentItem()
        selected_text = item.text()
        if self.energy_form == 1:
            roll = randint(1,100)
            powers = list(powerlists.energy_emission_powers_list.keys())
            roll_thresholds = [11, 21, 23, 35, 38, 43, 53, 63, 73, 76, 79, 84, 
                            94, 101]
            index = bisect(roll_thresholds, roll)
            power = powers[index]
            table = self.physicalforms[selected_text]
            roll = randint(1,100)
            rank_index = self.ability_roll(table, roll)
            rank = self.ranks[rank_index]
            score = self.min_std_rank_score(rank)
            epoint = self.energy_emission_body_part()
            self.powers_listbox.addItem(f"{power} - {rank} ({score}); emitted from {epoint}")
            item = self.powers_listbox.item(0)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

        if self.deity_travel_power == 1:
            roll = randint(1,100)
            powers = list(powerlists.travel_powers_list.keys())
            roll_thresholds = [3, 7, 11, 13, 15, 20, 27, 29, 35, 43, 47, 52, 57,
                            59, 65, 73, 77, 79, 81, 83, 94, 98, 99, 101]
            index = bisect(roll_thresholds, roll)
            power = powers[index]
            table = self.physicalforms[selected_text]
            roll = randint(1,100)
            rank_index = self.ability_roll(table, roll)
            rank = self.ranks[rank_index]
            score = self.min_std_rank_score(rank)
            epoint = self.energy_emission_body_part()
            self.powers_listbox.addItem(f"{power} - {rank} ({score})")
            item = self.powers_listbox.item(0)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        
        if self.wings_travel_power == 1:
            table = self.physicalforms[selected_text]
            roll = randint(1,100)
            rank_index = self.ability_roll(table, roll)
            rank = self.ranks[rank_index]
            score = self.min_std_rank_score(rank)
            epoint = self.energy_emission_body_part()
            self.powers_listbox.addItem(f"Winged Flight - {rank} ({score})")
            item = self.powers_listbox.item(0)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

        self.power_rank_above_remarkable = 0
        #roll number of powers
        print("Rolling Number of Powers and Power Classes!")
        self.roll_number_powers("powers")
        min = self.number_of_powers["min"]
        max = self.number_of_powers["max"]
        print(f"Number of powers - min={min} / max={max}")
        #add power class to the list for each minimum power number slot
        while min > 0:
            print(f"min={min}")
            power_class = self.roll_power_class()
            self.power_classes_listbox.addItem(power_class)
            min -= 1
            print(f"min={min}")
        #set the min to 0 to start adding from 0 when powers are added to the list
        min = self.powers_listbox.count()
        self.number_of_powers["min"] = min
        self.num_powers_label.setText(f"Min: {min} / Max: {max}")
        #enable buy and remove buttons
        self.buy_power_button.setEnabled(True)
        self.remove_power_button.setEnabled(True)
        self.power_classes_listbox.setFocus()
        #if powers were purchased for Resources, reset back to original Resources
        if len(self.purchased_powers) > 0:
            print("Resources were spent on Powers, resetting...")
            self.purchased_powers = []
            resources_text = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            new_rank = self.ranks[self.original_resources_rank]
            resources_text.setText(new_rank)
            self.resources_rank = self.original_resources_rank
            print(f"resource_rank={self.resources_rank}")
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][1]))



    #Click the Buy Powers button
    def buy_power(self):
        #first check if there are enough resources and reduce resources by two 
        #ranks or if buying a power will exceed the maximum number of powers 
        #and display the new rank and score on the Abilities tab
        print("Buying Power!")
        print(f"resource_rank={self.resources_rank}")
        current_resources = self.resources_rank
        new_resources = current_resources - 2
        num_powers = self.power_classes_listbox.count()
        max_powers = self.number_of_powers["max"]
        print(f"current_resources={current_resources}, new_resources={new_resources}")
        if new_resources < 0:
            print("Not enough resources!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Resources!", "You do not have enough Resources to purchase another power!", "warning", buttons=0)
        elif num_powers == max_powers:
            print("Not enough power slots!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Power Slots!", "You do not have enough Power slots to purchase another power!", "warning", buttons=0)
        else:
            new_rank = self.ranks[new_resources]
            resources_text = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            resources_text.setText(new_rank)
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][1]))
            
            #roll an additional power class and add it to the list
            print("Adding Power!")
            power_class = self.roll_power_class()
            self.power_classes_listbox.addItem(power_class)
            self.purchased_powers.append(power_class)
            self.resources_rank -= 2
            print(f"resources_rank={self.resources_rank}")



    #Click the Remove Powers button
    def remove_power(self):
        print("Removing Power...")
        print(f"resource_rank={self.resources_rank}")
        #Add a check if a power class was selected first
        selected_items = self.power_classes_listbox.selectedItems()
        if not selected_items:
            self.display_message(resource_path('images/oops.jpg'), "No Power Class Selected!", "You need to select a Power Class to remove!", "warning", buttons=0)
        else:
            result = self.display_message(resource_path('images/question.jpg'), "Confirm Removing Power", "Are you sure you want to remove this power class?", "question", buttons=1)
            if result == QMessageBox.Ok:
                print("User clicked OK")
                power = self.power_classes_listbox.currentRow()
                power_item = self.power_classes_listbox.item(power)
                power_text = power_item.text()
                print(f"Removing power{power}, power_item={power_item}, power_text={power_text}")

                #if removed power is a purchased power return the Resources spent
                if power_text in self.purchased_powers:
                    self.purchased_powers.remove(power_text)
                    current_resources = self.resources_rank
                    new_resources = current_resources + 2
                    resources_text = self.secondary_ability_inputs["resources"]["rank"]
                    resources_score_text = self.secondary_ability_inputs["resources"]["score"]
                    new_rank = self.ranks[new_resources]
                    resources_text.setText(new_rank)
                    self.resources_rank = new_resources
                    print(f"resource_rank={self.resources_rank}")
                    if self.std_rank_scores == 0:
                        #minimum rank scores
                        resources_score_text.setText(str(self.rank_scores[new_rank][0]))
                    else:
                        #standard rank scores
                        resources_score_text.setText(str(self.rank_scores[new_rank][1]))

                self.power_classes_listbox.takeItem(power)
                #if the last power class was removed disable the roll and add power 
                #buttons and enable the generate weakness button
                if self.power_classes_listbox.count() == 0:
                        self.generate_weakness_button.setEnabled(True)
                        self.roll_power_button.setEnabled(False)
                        self.add_power_button.setEnabled(False)
                        self.bonus_powers_listbox.clear()
                        self.optional_powers_listbox.clear()
                        self.power_textbox.clear()
            elif result == QMessageBox.Cancel:
                print("User clicked Cancel")



    #Click the Power Classes List
    def power_classes_list_selected(self):
        #activate the Roll Power button and clear the Power, Bonus and Optional boxes
        self.roll_power_button.setEnabled(True)
        self.roll_power_button.setFocus()
        self.power_textbox.clear()
        self.bonus_powers_listbox.clear()
        self.optional_powers_listbox.clear()



    #Click the Roll Powers button
    def roll_power(self):
        print("Rolling Power...")
        print(f"resource_rank={self.resources_rank}")
        #reset the bonus and optional power list boxes
        self.bonus_powers_listbox.clear()
        self.optional_powers_listbox.clear()

        self.villain_bubble_pixmap = QPixmap(resource_path('images/thanos_bubble.jpg'))
        self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
        self.villain_pixmap = QPixmap(resource_path('images/thanos.jpg'))
        self.villain_image.setPixmap(self.villain_pixmap)

        #roll and determine power from power class
        print("Rolling Power!")
        roll = randint(1,100)
        item = self.power_classes_listbox.currentItem()
        power_class = item.text()
        print(f"power_class={power_class}, roll={roll}")
        if power_class == "Defensive":
            powers = list(powerlists.defensive_powers_list.keys())
            roll_thresholds = [16, 21, 24, 31, 36, 41, 49, 51, 54, 66, 71, 78, 
                               83, 88, 95, 98, 101]
            #match the index of the roll threshold with the index of the power 
            #in the power class to get the name of the power
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            #get the bonus and optional powers and fill in the appropriate listboxes 
            #repeat for each power class below...
            self.get_bonus_optional_powers(powerlists.defensive_powers_list, powername)
        elif power_class == "Detection":
            powers = list(powerlists.detection_powers_list.keys())
            roll_thresholds = [3, 5, 11, 15, 21, 29, 35, 41, 43, 45, 51, 55, 57,
                                59, 60, 63, 70, 80, 91, 95, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.detection_powers_list, powername)
        elif power_class == "Energy Control":
            powers = list(powerlists.energy_control_powers_list.keys())
            roll_thresholds = [8, 11, 16, 19, 26, 29, 32, 37, 39, 46, 50, 54, 60,
                               67, 74, 78, 81, 85, 91, 98, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.energy_control_powers_list, powername)
        elif power_class == "Energy Emission":
            powers = list(powerlists.energy_emission_powers_list.keys())
            roll_thresholds = [11, 21, 23, 35, 38, 43, 53, 63, 73, 76, 79, 84, 
                               94, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.energy_emission_powers_list, powername)
        elif power_class == "Fighting":
            powers = list(powerlists.fighting_powers_list.keys())
            print("Available Powers:", powers)
            roll_thresholds = [21, 61, 76, 81, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.fighting_powers_list, powername)
        elif power_class == "Illusory":
            powers = list(powerlists.illusory_powers_list.keys())
            roll_thresholds = [16, 71, 86, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.illusory_powers_list, powername)
        elif power_class == "Lifeform Control":
            powers = list(powerlists.lifeform_control_powers_list.keys())
            roll_thresholds = [15, 16, 19, 27, 33, 35, 36, 40, 52, 61, 63, 66, 67,
                                70, 72, 81, 84, 90, 91, 96, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.lifeform_control_powers_list, powername)
        elif power_class == "Magical":
            powers = list(powerlists.magic_powers_list.keys())
            roll_thresholds = [9, 16, 18, 26, 29, 34, 40, 42, 72, 78, 80, 96, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.magic_powers_list, powername)
        elif power_class == "Matter Control":
            powers = list(powerlists.matter_control_powers_list.keys())
            roll_thresholds = [6, 18, 23, 30, 40, 47, 52, 62, 69, 74, 84, 94, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.matter_control_powers_list, powername)
        elif power_class == "Matter Conversion":
            powers = list(powerlists.matter_conversion_powers_list.keys())
            roll_thresholds = [11, 26, 46, 71, 81, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.matter_conversion_powers_list, powername)
        elif power_class == "Matter Creation":
            powers = list(powerlists.matter_creation_powers_list.keys())
            roll_thresholds = [11, 25, 30, 36, 60, 70, 89, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.matter_creation_powers_list, powername)
        elif power_class == "Mental Enhancement":
            powers = list(powerlists.mental_enhancement_powers_list.keys())
            roll_thresholds = [5, 9, 12, 13, 14, 16, 17, 23, 24, 27, 28, 32, 41,
                                48, 49, 59, 66, 67, 68, 70, 73, 74, 75, 76, 77, 
                                79, 80, 81, 82, 86, 87, 97, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.mental_enhancement_powers_list, powername)
        elif power_class == "Physical Enhancement":
            powers = list(powerlists.physical_enhancement_powers_list.keys())
            roll_thresholds = [15, 29, 31, 34, 41, 43, 46, 48, 61, 63, 68, 72, 77,
                                79, 83, 91, 95, 97, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.physical_enhancement_powers_list, powername)
        elif power_class == "Power Control":
            powers = list(powerlists.power_control_powers_list.keys())
            roll_thresholds = [9, 13, 19, 24, 38, 40, 50, 56, 61, 65, 74, 84, 97,
                                101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.power_control_powers_list, powername)
        elif power_class == "Self-Alteration":
            powers = list(powerlists.self_alteration_powers_list.keys())
            roll_thresholds = [3, 10, 11, 14, 20, 21, 28, 31, 34, 38, 39, 43, 45,
                                50, 56, 58, 59, 61, 62, 63, 64, 68, 71, 72, 75,
                                79, 82, 85, 91, 95, 100, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.self_alteration_powers_list, powername)
        elif power_class == "Travel":
            powers = list(powerlists.travel_powers_list.keys())
            roll_thresholds = [3, 7, 11, 13, 15, 20, 27, 29, 35, 43, 47, 52, 57,
                                59, 65, 73, 77, 79, 81, 83, 94, 98, 99, 101]
            powername = self.get_power(roll, roll_thresholds, powers)
            print(f"powername={powername}")
            self.get_bonus_optional_powers(powerlists.travel_powers_list, powername)

        self.add_power_button.setEnabled(True)



    #determine the power from the roll and insert the name in the Power textbox
    def get_power(self, roll, roll_thresholds, powers):
        print("Getting power....")
        #The bisect function uses efficient lookup and finds the correct index 
        #in roll_thresholds, which directly maps to the correct power
        print(f"powers={powers}")
        index = bisect(roll_thresholds, roll)
        power = powers[index]
        print(f"power={power}")
        self.power_textbox.setText(power)
        return power
    



    #lookup the power in the dictionary and check if it has bonus/optional 
    #powers and display them in the appropriate boxes
    def get_bonus_optional_powers(self, powerslist, powername):
        for power, data in powerslist.items():
            if power == powername and len(data) > 1:  # Check if there's a dictionary with extra properties
                bonus_powers = data[1].get("bonus", [])
                option_powers = data[1].get("option", [])
                
                has_bonus = bool(bonus_powers)  # True if list is not empty
                has_option = bool(option_powers)  # True if list is not empty
                
                if has_bonus:
                    for bonus_power in bonus_powers:
                        self.bonus_powers_listbox.addItem(bonus_power)
                if has_option:
                    for option_power in option_powers:
                        self.optional_powers_listbox.addItem(option_power)



    #Click the Add Power button
    #Roll the rank of the power and add the power and any bonus and optional 
    #powers to the Powers list and update the min/max label
    def add_power(self):
        #get the power name and power class
        power = self.power_textbox.text()
        power_class_item = self.power_classes_listbox.currentItem()
        power_class = power_class_item.text()
        print(f"****** Adding {power} ********")
        print(f"resource_rank={self.resources_rank}")
        #if there are items in the bonus list box and none are selected
        bonus_powers = self.bonus_powers_listbox.count()
        if not self.bonus_powers_listbox.selectedItems() and bonus_powers:
            print("Bonus Power not selected!")
            self.display_message(resource_path('images/oops.jpg'), "Bonus Power Not Selected!", "You need to select a Bonus Power!", "warning", buttons=0)

        else:
            #check if the powers selected exceeds the number of available power slots
            min = self.number_of_powers["min"]
            max = self.number_of_powers["max"]
            print(f"getting cost of currently selected powers...")
            print(f"powerclass={power_class}, powername={power}")
            #get the power class dictionary to look up the power cost
            powerlist = powerlists.all_power_lists[power_class]
            #get the cost of the main power if there is one; 
            #user may be adding just a bonus or optional power
            if power != '':
                cost = powerlist[power][0]
                print(f"powercost={cost}")
            else:
                cost = 0
            #find the cost of any bonus and/or optional powers selected
            bonus_powers_selected = self.bonus_powers_listbox.selectedItems()
            option_powers_selected = self.optional_powers_listbox.selectedItems()
            if bonus_powers_selected:
                for bonus_power in bonus_powers_selected:
                    bonus_power_text = bonus_power.text()
                    if "*" in bonus_power_text:
                        cost += 2
                    else:
                        cost += 1
            if option_powers_selected:
                for option_power in option_powers_selected:
                    option_power_text = option_power.text()
                    if "*" in option_power_text:
                        cost += 2
                    else:
                        cost += 1
                    #Power Classes are not added to the cost but are added to the Power Classes List
                    if option_power_text == "Energy Control" or option_power_text == "Energy Emission" or option_power_text == "Magical Power":
                        cost -= 1
            print(f"powercost={cost}, min={min}/max={max}")
            cost += min #add the cost of the power(s) and the current minimum slots used
            print(f"powercost+min={cost}, min={min}/max={max}")
            if cost > max: #cost exceeds the maximum number of powers display a warning message
                print("Not enough power slots available!")
                self.display_message(resource_path('images/oops.jpg'), "Not Enough Power Slots!", "You do not have enough Power slots to add this power!", "warning", buttons=0)

            else:#roll the power ranks and add them to the Powers List and update the min/max
                #roll the rank for the main power and display it in the Powers list
                roll = randint(1,100)
                item = self.physical_form_list.currentItem()
                selected_text = item.text()
                table = self.physicalforms[selected_text]
                #if one of the two physical forms with a table that depends on 
                #the optional form, get the table for the optional form
                if selected_text == "Demihuman-Avian":
                    current_row = self.options_list.currentRow()
                    print(current_row)
                    if current_row == 0:
                        table = self.physicalforms[selected_text]["Angelic"]
                    else:
                        table = self.physicalforms[selected_text]["Harpy"]
                if selected_text == "Animal":
                    current_row = self.options_list.currentRow()
                    print(current_row)
                    if current_row == 0:
                        table = self.physicalforms[selected_text]["Terrestrial"]
                    else:
                        table = self.physicalforms[selected_text]["Extraterrestrial"]

                rank_index = self.ability_roll(table, roll)
                #check if the Power Rank is above Remarkable and flag it for the
                #possibility of a Fatal Weakness
                if rank_index > 6:
                    self.power_rank_above_remarkable = 1

                rank = self.ranks[rank_index]
                score = self.min_std_rank_score(rank)
                print(f"roll={roll}, rank={rank}\{rank_index}, score={score}")
                if power != '':
                    if power_class == "Energy Emission":
                        epoint = self.energy_emission_body_part()
                        self.powers_listbox.addItem(f"{power} - {rank} ({score}); emitted from {epoint}")
                    elif power == "Biophysical Control*":#show the option window
                        dialog = BiophysicalOptionDialog(self)
                        if dialog.exec_():#get the user's selected option
                            selected_option = dialog.get_selected_option()
                            if selected_option == "Random":#if random was selected roll the option
                                selected_option = self.biophysical_random_option()
                            if selected_option:
                                self.powers_listbox.addItem(f"{power} ({selected_option}) - {rank} ({score})")
                    else:
                        self.powers_listbox.addItem(f"{power} - {rank} ({score})")

                #roll the power ranks for the bonus powers
                for bonus_power in bonus_powers_selected:
                    roll = randint(1,100)
                    rank_index = self.ability_roll(table, roll)
                    rank = self.ranks[rank_index]
                    score = self.min_std_rank_score(rank)
                    bonus_power_name = bonus_power.text()
                    print(f"roll={roll}, rank={rank}\{rank_index}, score={score}")
                    #if energy emission power check for emission point
                    if bonus_power_name in powerlists.energy_emission_powers_list.keys():
                        epoint = self.energy_emission_body_part()
                        self.powers_listbox.addItem(f"{bonus_power_name} - {rank} ({score}); emitted from {epoint}")
                    else:
                        self.powers_listbox.addItem(f"{bonus_power_name} - {rank} ({score})")
                self.bonus_powers_listbox.clear()
                #roll the power ranks fore the optional powers
                for option_power in option_powers_selected:
                    roll = randint(1,100)
                    rank_index = self.ability_roll(table, roll)
                    rank = self.ranks[rank_index]
                    score = self.min_std_rank_score(rank)
                    option_power_name = option_power.text()
                    print(f"roll={roll}, rank={rank}\{rank_index}, score={score}")
                    #if the optional power is a power class add it to the Power Class list and not the Powers list
                    if option_power_name != "Energy Emission" and option_power_name != "Energy Control" and option_power_name != "Magical Power":
                        #if energy emission power check for emission point
                        if option_power_name in powerlists.energy_emission_powers_list.keys():
                            epoint = self.energy_emission_body_part()
                            self.powers_listbox.addItem(f"{option_power_name} - {rank} ({score}); emitted from {epoint}")
                        elif option_power_name == "Biophysical Control*":#show the option window
                            dialog = BiophysicalOptionDialog(self)
                            if dialog.exec_():#get the user's selected option
                                selected_option = dialog.get_selected_option()
                                if selected_option == "Random":#if random was selected roll the option
                                    selected_option = self.biophysical_random_option()
                                if selected_option:
                                    self.powers_listbox.addItem(f"{power} ({selected_option}) - {rank} ({score})")
                        else:
                            self.powers_listbox.addItem(f"{option_power_name} - {rank} ({score})")
                    elif option_power_name == "Magical Power":#convert Magical Power to Magical when adding it to the Power Classes list
                        self.power_classes_listbox.addItem("Magical")
                    else:
                        self.power_classes_listbox.addItem(option_power_name)

                    #self.optional_powers_listbox.takeItem(self.optional_powers_listbox.row(option_power))
                self.optional_powers_listbox.clear()
                    
                #calculate the new min power slots and update the label
                self.number_of_powers["min"] = cost
                self.num_powers_label.setText(f"Min: {cost} / Max: {max}")

                #remove the selected powers and remove the power class; 
                #If the Power Classes list is empty enable the generate weakness button,
                #disable the roll and add power buttons (they will be re-enabled if the 
                #user uses the Power Classes button) and empty the bonus and optional power lists
                self.power_textbox.clear()
                self.power_classes_listbox.takeItem(self.power_classes_listbox.row(power_class_item))
                self.add_power_button.setEnabled(False)
                if self.power_classes_listbox.count() == 0:#Power Class list is empty
                    self.generate_weakness_button.setEnabled(True)
                    self.roll_power_button.setEnabled(False)
                    self.add_power_button.setEnabled(False)
                    self.bonus_powers_listbox.clear()
                    self.optional_powers_listbox.clear()
                    self.generate_weakness_button.setFocus()
                    self.villain_bubble_pixmap = QPixmap(resource_path('images/superskrull_bubble.jpg'))
                    self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
                    self.villain_pixmap = QPixmap(resource_path('images/superskrull.jpg'))
                    self.villain_image.setPixmap(self.villain_pixmap)
                elif cost == max:#maximum number of Power slots has been used
                    self.villain_bubble_pixmap = QPixmap(resource_path('images/kang_bubble.jpg'))
                    self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
                    self.villain_pixmap = QPixmap(resource_path('images/kang.jpg'))
                    self.villain_image.setPixmap(self.villain_pixmap)
                else:#continue selecting a class until the Power Class list is empty
                    self.power_classes_listbox.setFocus()
                    self.villain_bubble_pixmap = QPixmap(resource_path('images/ultron_bubble.jpg'))
                    self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
                    self.villain_pixmap = QPixmap(resource_path('images/ultron.jpg'))
                    self.villain_image.setPixmap(self.villain_pixmap)
                


    #Click the Powers list; prompts user to remove the selected power
    def powers_list_selected(self, power_item):
        if power_item.flags() & Qt.ItemIsEnabled:
            result = self.display_message(resource_path('images/question.jpg'), "Confirm Removing Power", "Are you sure you want to remove this power?", "question", buttons=1)
            if result == QMessageBox.Ok:
                print("User clicked OK")
                #refund a power slot depending on how much the power cost (if it has a *)
                min = self.number_of_powers["min"]
                max = self.number_of_powers["max"]
                print(f"Number of powers - min={min} / max={max}")
                power_text = power_item.text()
                print(f"power_item={power_item} / power_text={power_text}")
                if "*" in power_text:
                    min -= 2
                else:
                    min -= 1
                self.number_of_powers["min"] = min
                self.num_powers_label.setText(f"Min: {min} / Max: {max}")
                power = self.powers_listbox.currentRow()
                self.powers_listbox.takeItem(power)
            elif result == QMessageBox.Cancel:
                print("User clicked Cancel")



    #Click the Generate Weakness button
    def generate_weakness(self):
        #Roll Stimulus
        s_roll = randint(1, 100)
        if s_roll < 14:
            stimulus = "Elemental Allergy"
        elif s_roll < 19:
            stimulus = "Molecular Allergy"
        elif s_roll < 44:
            stimulus = "Energy Allergy"
        elif s_roll < 69:
            stimulus = "Energy Depletion"
        elif s_roll < 82:
            stimulus = "Energy Dampening"
        elif s_roll < 95:
            stimulus = "Finite Limit"
        else:
            stimulus = "Psychological"
        
        #Roll Effect
        e_roll = randint(1, 100)
        if e_roll < 51:
            effect = "Power Negation"
        elif e_roll < 91:
            effect = "Incapacitation"
        elif self.power_rank_above_remarkable:
            effect = "Fatal"
        else:
            effect = "Incapacitation"

        #Roll Duration
        d_roll = randint(1, 100)
        if d_roll < 41:
            duration = "Continuous with Contact"
        elif d_roll < 61:
            duration = "Limited Duration with Contact"
        elif d_roll < 61:
            duration = "Limited Duration after Contact"
        else:
            duration = "Permanent"

        #add to the Weakness textboxes on the Powers tab and Physical Forms tab
        self.powers_weakness_textbox.insertPlainText(f"{stimulus} causes {effect} that is {duration}")
        self.weakness_textbox.insertPlainText(f"{stimulus} causes {effect} that is {duration}")

        #disable the rest of the buttons on the Powers tab and enable the Talents tab
        self.generate_weakness_button.setEnabled(False)
        self.roll_power_classes_button.setEnabled(False)
        self.buy_power_button.setEnabled(False)
        self.remove_power_button.setEnabled(False)
        self.roll_talent_classes_button.setEnabled(True)
        self.powers_listbox.setEnabled(False)
        self.roll_talent_classes_button.setFocus()

        self.villain_bubble_pixmap = QPixmap(resource_path('images/juggernaut_bubble.jpg'))
        self.villain_bubble_image.setPixmap(self.villain_bubble_pixmap)
        self.villain_pixmap = QPixmap(resource_path('images/juggernaut.jpg'))
        self.villain_image.setPixmap(self.villain_pixmap)
        self.talent_pixmap = QPixmap(resource_path('images/punisher.jpg'))
        self.talent_image.setPixmap(self.talent_pixmap)



    #Click the Roll Talent Classes button
    def roll_talent_classes(self):
        print("Rolling Talent Classes...")
        print(f"resource_rank={self.resources_rank}")
        self.talent_classes_listbox.clear()
        self.roll_talent_button.setEnabled(False)
        self.select_talent_listbox.clear()
        self.talents_listbox.clear()
        self.roll_number_powers("talents")
        min = self.number_of_talents["min"]
        max = self.number_of_talents["max"]
        print(f"Number of talents - min={min} / max={max}")
        if min == 0:
            self.roll_contact_classes_button.setEnabled(True)
            self.talent2_pixmap = QPixmap(resource_path('images/capt_marvel.jpg'))
            self.talent2_image.setPixmap(self.talent2_pixmap)
            self.contact_pixmap = QPixmap(resource_path('images/wolverine.jpg'))
            self.contact_image.setPixmap(self.contact_pixmap)
        else:
            self.roll_contact_classes_button.setEnabled(False)
            self.talent2_pixmap = QPixmap(resource_path('images/spidey.jpg'))
            self.talent2_image.setPixmap(self.talent2_pixmap)
        #add talent class to the list for each minimum talent number slot
        while min > 0:
            print(f"min={min}")
            self.roll_talent_class()
            min -= 1
            print(f"min={min}")
        #set the min to 0 to start adding from 0 when talents are added to the list
        self.number_of_talents["min"] = min
        self.num_talents_label.setText(f"Min: {min} / Max: {max}")
        #enable buy and remove buttons
        self.buy_talent_button.setEnabled(True)
        self.remove_talent_button.setEnabled(True)
        self.talent_classes_listbox.setFocus()
        self.talent_pixmap = QPixmap("")
        self.talent_image.setPixmap(self.talent_pixmap)
        #if talents were purchased for Resources, reset back to original Resources
        if self.talent_bought:
            print("Resources were spent on Talents, resetting...")
            #get the current index of the current Resource rank
            resources_item = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            resources_text = resources_item.text()
            index = self.ranks.index(resources_text)
            #return the spent resources and update the textboxes
            new_rank_index = index + self.talent_bought
            self.resources_rank = new_rank_index
            print(f"resource_rank={self.resources_rank}")
            new_rank_name = self.ranks[new_rank_index]
            print(f"resources_item{resources_item} / resources_score_text={resources_score_text}")
            print(f"resources_text={resources_text} / index={index}")
            print(f"new_rank_index={new_rank_index} / new_rank_name={new_rank_name}")
            resources_item.setText(new_rank_name)
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank_name][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank_name][1]))
            self.talent_bought = 0
        print(f"self.talent_bought={self.talent_bought}")



    #Click the Buy Talents button
    def buy_talent(self):
        #first check if there are enough resources and reduce resources by one 
        #rank or if buying a talent will exceed the maximum number of talents
        #and display the new rank and score on the Abilities tab
        print("Buying Talent!")
        print(f"resource_rank={self.resources_rank}")
        current_resources = self.resources_rank
        new_resources = current_resources - 1
        num_talents = self.talent_classes_listbox.count()
        max_talents = self.number_of_talents["max"]
        print(f"current_resources={current_resources}, new_resources={new_resources}")
        if new_resources < 0:
            print("Not enough resources!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Resources!", "You do not have enough Resources to purchase another talent!", "warning", buttons=0)
        elif num_talents == max_talents:
            print("Not enough talent slots!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Talent Slots!", "You do not have enough Talent slots to purchase another talent!", "warning", buttons=0)
        else:
            new_rank = self.ranks[new_resources]
            resources_text = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            resources_text.setText(new_rank)
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][1]))
            
            #roll an additional talent class and add it to the list
            print("Adding Talent!")
            self.roll_talent_class()
            self.talent_bought += 1
            self.resources_rank -= 1
            print(f"resources_rank={self.resources_rank}")
            print(f"self.talent_bought={self.talent_bought}")
            self.talent2_pixmap = QPixmap(resource_path('images/spidey.jpg'))
            self.talent2_image.setPixmap(self.talent2_pixmap)



    #Click the Remove Talnets button
    def remove_talent(self):
        print("Removing Talent...")
        print(f"resource_rank={self.resources_rank}")
        #Add a check if a power class was selected first
        selected_items = self.talent_classes_listbox.selectedItems()
        if not selected_items:
            self.display_message(resource_path('images/oops.jpg'), "No Talent Class Selected!", "You need to select a Talent Class to remove!", "warning", buttons=0)
        else:
            result = self.display_message(resource_path('images/question.jpg'), "Confirm Removing Talent", "Are you sure you want to remove this talent class?", "question", buttons=1)
            if result == QMessageBox.Ok:
                print("User clicked OK")
                power = self.talent_classes_listbox.currentRow()
                self.talent_classes_listbox.takeItem(power)
                #if the last power class was removed disable the roll and add power 
                #buttons and enable the generate weakness button
                if self.talent_classes_listbox.count() == 0:
                    print("The last Talent Class was removed from the list")
            elif result == QMessageBox.Cancel:
                print("User clicked Cancel")



    #Click or hit Enter on an item in the Talent Classes listbox
    def talent_classes_list_selected(self):
        self.roll_talent_button.setEnabled(True)
        self.roll_talent_button.setFocus()



    #Click the Roll Talent button
    def roll_talent(self):
        #roll and determine talent from talent class
        print("Rolling Talent!")
        print(f"resource_rank={self.resources_rank}")
        roll = randint(1,10)
        item = self.talent_classes_listbox.currentItem()
        talent_class = item.text()
        self.select_talent_listbox.clear()
        self.select_talent_listbox.setFocus()
        self.talent2_pixmap = QPixmap(resource_path('images/scarlet_witch.jpg'))
        self.talent2_image.setPixmap(self.talent2_pixmap)
        print(f"talent_class={talent_class}, roll={roll}")
        if talent_class == "Weapon Skills":
            if roll < 3:
                self.select_talent_listbox.addItem("Guns")
            elif roll < 6:
                self.select_talent_listbox.addItem("Thrown Weapons")
            elif roll < 7:
                self.select_talent_listbox.addItem("Bows")
            elif roll < 9:
                self.select_talent_listbox.addItem("Blunt Weapons")
            elif roll < 10:
                self.select_talent_listbox.addItem("Sharp Weapons")
            else:
                self.select_talent_listbox.addItem("Oriental Weapons")
                self.select_talent_listbox.addItem("Marksman*")
                self.select_talent_listbox.addItem("Weapons Master*")
                self.select_talent_listbox.addItem("Weapon Specialist*")
        if talent_class == "Fighting Skills":
            if roll == 1:
                self.select_talent_listbox.addItem("Martial Arts A")
            elif roll == 2:
                self.select_talent_listbox.addItem("Martial Arts B")
            elif roll == 3:
                self.select_talent_listbox.addItem("Martial Arts C")
            elif roll == 4:
                self.select_talent_listbox.addItem("Martial Arts D")
            elif roll == 5:
                self.select_talent_listbox.addItem("Martial Arts E")
            elif roll == 6:
                self.select_talent_listbox.addItem("Wrestling")
            elif roll == 7:
                self.select_talent_listbox.addItem("Thrown Objects")
            elif roll == 8:
                self.select_talent_listbox.addItem("Tumbling")
            else:
                self.select_talent_listbox.addItem("Acrobatics")
        if talent_class == "Professional Skills":
            if roll == 1:
                self.select_talent_listbox.addItem("Medicine*")
            elif roll == 2:
                self.select_talent_listbox.addItem("Law")
                self.select_talent_listbox.addItem("Law Enforcement")
            elif roll == 3:
                self.select_talent_listbox.addItem("Pilot")
            elif roll == 4:
                self.select_talent_listbox.addItem("Military")
            elif roll == 5:
                self.select_talent_listbox.addItem("Business/Finance")
            elif roll == 6:
                self.select_talent_listbox.addItem("Journalism")
            elif roll == 7:
                self.select_talent_listbox.addItem("Engineering")
            elif roll == 8:
                self.select_talent_listbox.addItem("Crime")
            elif roll == 9:
                self.select_talent_listbox.addItem("Psychiatry")
            else:
                self.select_talent_listbox.addItem("Detective/Espionage")
        if talent_class == "Scientific Skills":
            if roll < 3:
                self.select_talent_listbox.addItem("Chemistry")
            elif roll < 5:
                self.select_talent_listbox.addItem("Biology")
            elif roll < 7:
                self.select_talent_listbox.addItem("Geology")
            elif roll == 7:
                self.select_talent_listbox.addItem("Genetics")
            elif roll == 8:
                self.select_talent_listbox.addItem("Archeology")
            elif roll == 9:
                self.select_talent_listbox.addItem("Physics")
                self.select_talent_listbox.addItem("Computers")
            else:
                self.select_talent_listbox.addItem("Electronics")
        if talent_class == "Mystical and Mental Skills":
            if roll < 3:
                self.select_talent_listbox.addItem("Trance")
            elif roll < 6:
                self.select_talent_listbox.addItem("Mesmirsm and Hypnosis")
            elif roll < 8:
                self.select_talent_listbox.addItem("Sleight of Hand")
            elif roll < 10:
                self.select_talent_listbox.addItem("Resist Domination")
                self.select_talent_listbox.addItem("Mystic Origin*")
            else:
                self.select_talent_listbox.addItem("Occult Lore")
        if talent_class == "Other Skills":
            if roll < 3:
                self.select_talent_listbox.addItem("Artist")
            elif roll < 5:
                self.select_talent_listbox.addItem("Languages")
            elif roll < 7:
                self.select_talent_listbox.addItem("First Aid")
            elif roll < 9:
                self.select_talent_listbox.addItem("Repair/Tinkering")
            else:
                self.select_talent_listbox.addItem("Trivia")
                self.select_talent_listbox.addItem("Performer")
                self.select_talent_listbox.addItem("Animal Training*")
                self.select_talent_listbox.addItem("Heir to Fortune*")
                self.select_talent_listbox.addItem("Student*")
                self.select_talent_listbox.addItem("Leadership*")

    

    #Click or hit Enter on an item in the Select Talent listbox
    def select_talent_selected(self, selected_talent):
        #confirm the user wants to add the Talent
        result = self.display_message(resource_path('images/question.jpg'), "Confirm Adding Talent", "Are you sure you want to add this Talent to the character?", "question", buttons=1)
        if result == QMessageBox.Ok:
            print("User clicked OK")
            #check if the talent selected exceeds the number of available talent slots
            min = self.number_of_talents["min"]
            max = self.number_of_talents["max"]
            print(f"getting cost of currently selected talent...")
            cost = 0
            selected_talent_text = selected_talent.text()
            if "*" in selected_talent_text:
                cost += 2
            else:
                cost += 1
            print(f"talentcost={cost}, min={min}/max={max}")
            cost += min #add the cost of the talent and the current minimum slots used
            print(f"talentcost+min={cost}, min={min}/max={max}")
            if cost > max: #cost exceeds the maximum number of powers display a warning message
                print("Not enough talent slots available!")
                self.display_message(resource_path('images/oops.jpg'), "Not Enough Talent Slots!", "You do not have enough Talent slots to add this Talent!", "warning", buttons=0)
            else:
                talent_class = self.talent_classes_listbox.currentRow()
                self.talent_classes_listbox.takeItem(talent_class)
                self.select_talent_listbox.clear()
                self.talents_listbox.addItem(selected_talent_text)
                #calculate the new min talent slots and update the label
                self.number_of_talents["min"] = cost
                self.num_talents_label.setText(f"Min: {cost} / Max: {max}")
                #if the last Talent class was removed disable the talent classes
                #and roll talent buttons and enable the Contacts tab 
                if self.talent_classes_listbox.count() == 0:
                    if cost == max:
                        self.roll_talent_classes_button.setEnabled(False)
                        self.buy_talent_button.setEnabled(False)
                        self.remove_talent_button.setEnabled(False)
                        self.roll_contact_classes_button.setEnabled(True)
                        self.roll_contact_classes_button.setFocus()
                    else:
                        self.roll_contact_classes_button.setEnabled(True)

                    self.roll_talent_button.setEnabled(False)                        
                    self.talent2_pixmap = QPixmap(resource_path('images/beast.jpg'))
                    self.talent2_image.setPixmap(self.talent2_pixmap)
                    self.contact_pixmap = QPixmap(resource_path('images/wolverine.jpg'))
                    self.contact_image.setPixmap(self.contact_pixmap)
                else:
                    self.talent_classes_listbox.setFocus()
                    self.talent2_pixmap = QPixmap(resource_path('images/falcon.jpg'))
                    self.talent2_image.setPixmap(self.talent2_pixmap)
        elif result == QMessageBox.Cancel:
            print("User clicked Cancel")



    #Clicking or hitting Enter on Talent List
    def talent_list_selected(self, talent_item):
        #confirm removal of selected Talent
        result = self.display_message(resource_path('images/question.jpg'), "Confirm Removing Talent", "Are you sure you want to remove this talent?", "question", buttons=1)
        if result == QMessageBox.Ok:
            print("User clicked OK")
            #refund a power slot depending on how much the power cost (if it has a *)
            min = self.number_of_talents["min"]
            max = self.number_of_talents["max"]
            print(f"Number of talents - min={min} / max={max}")
            talent_text = talent_item.text()
            print(f"power_item={talent_item} / power_text={talent_text}")
            if "*" in talent_text:
                min -= 2
            else:
                min -= 1
            self.number_of_talents["min"] = min
            self.num_talents_label.setText(f"Min: {min} / Max: {max}")
            talent = self.talents_listbox.currentRow()
            self.talents_listbox.takeItem(talent)
        elif result == QMessageBox.Cancel:
            print("User clicked Cancel")

        

    #Click the Roll Contacts Button
    def roll_contact_classes(self):
        print("Rolling Contact Classes...")
        print(f"resource_rank={self.resources_rank}")
        self.contacts_classes_listbox.clear()
        self.select_contact_listbox.clear()
        self.roll_talent_classes_button.setEnabled(False)
        self.talents_listbox.setEnabled(False)
        self.talent2_pixmap = QPixmap("")
        self.talent2_image.setPixmap(self.talent2_pixmap)
        self.contact2_pixmap = QPixmap("")
        self.contact2_image.setPixmap(self.contact2_pixmap)
        
        if self.initial_contacts > 0:
            index = 0
            item = self.contacts_listbox.item(index)
            text = item.text()
            self.contacts_listbox.clear()
            self.contacts_listbox.addItem(text)
        else:
            self.contacts_listbox.clear()

        self.roll_number_powers("contacts")
        min = self.number_of_contacts["min"]
        max = self.number_of_contacts["max"]
        #if minimum contacts is 0 user has to buy contacts up to the max
        #check for initial contacts from the physical form
        if min == 0:#if initial contacts are 0 from physical form
            self.contacts_classes_listbox.setEnabled(False)
            self.contact2_pixmap = QPixmap(resource_path('images/uatu.jpg'))
            self.contact2_image.setPixmap(self.contact2_pixmap)
            self.contact_pixmap = QPixmap("")
            self.contact_image.setPixmap(self.contact_pixmap)
        elif self.initial_contacts == 1: #if initial contacts is 1 from physical form
            min = 1
            self.contact2_pixmap = QPixmap(resource_path('images/uatu.jpg'))
            self.contact2_image.setPixmap(self.contact2_pixmap)
            self.contact_pixmap = QPixmap("")
            self.contact_image.setPixmap(self.contact_pixmap)
        elif min == 1 and self.initial_contacts == 2:
            # if initial contacts is at least one from physical form and one was rolled as min
            self.contacts_classes_listbox.setEnabled(False)
            self.contact2_pixmap = QPixmap(resource_path('images/uatu.jpg'))
            self.contact2_image.setPixmap(self.contact2_pixmap)
            self.contact_pixmap = QPixmap("")
            self.contact_image.setPixmap(self.contact_pixmap)
        else:
            self.contacts_classes_listbox.setEnabled(True)
            self.contacts_classes_listbox.setFocus()
            self.contact_pixmap = QPixmap(resource_path('images/daredevil.jpg'))
            self.contact_image.setPixmap(self.contact_pixmap)
        #enable buy button
        self.buy_contact_button.setEnabled(True)

        #add contact classes to the list
        self.contacts_classes_listbox.addItem("Professional")
        self.contacts_classes_listbox.addItem("Scientific")
        self.contacts_classes_listbox.addItem("Political")
        self.contacts_classes_listbox.addItem("Mystic")

        #if contacts were purchased for Resources, reset back to original Resources
        if self.contact_bought:
            print("Resources were spent on Contacts, resetting...")
            #get the current index of the current Resource rank
            resources_item = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            resources_text = resources_item.text()
            index = self.ranks.index(resources_text)
            #return the spent resources and update the textboxes
            new_rank_index = index + self.contact_bought
            self.resources_rank = new_rank_index
            print(f"resource_rank={self.resources_rank}")
            new_rank_name = self.ranks[new_rank_index]
            print(f"resources_item{resources_item} / resources_score_text={resources_score_text}")
            print(f"resources_text={resources_text} / index={index}")
            print(f"new_rank_index={new_rank_index} / new_rank_name={new_rank_name}")
            resources_item.setText(new_rank_name)
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank_name][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank_name][1]))
            self.contact_bought = 0
        print(f"self.contact_bought={self.contact_bought}")
        if self.initial_contacts > 0:
            item = self.contacts_listbox.item(0)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        print(f"Number of contacts - min={min} / max={max}")
        self.num_contacts_label.setText(f"Min: {min} / Max: {max}")



    def contact_class_list_selected(self, item):
        self.select_contact_listbox.clear()
        self.select_contact_listbox.setFocus()
        contact_class = item.text()
        if contact_class == "Professional":
            for contact in powerlists.professional_contacts:
                self.select_contact_listbox.addItem(contact)
        elif contact_class == "Scientific":
            for contact in powerlists.scientific_contacts:
                self.select_contact_listbox.addItem(contact)
        elif contact_class == "Political":
            for contact in powerlists.political_contacts:
                self.select_contact_listbox.addItem(contact)
        elif contact_class == "Mystic":
            for contact in powerlists.mystic_contact:
                self.select_contact_listbox.addItem(contact)



    def select_contact_list_selected(self, selected_contact):
        #confirm the user wants to add the Contact
        result = self.display_message(resource_path('images/question.jpg'), "Confirm Adding Contact", "Are you sure you want to add this Contact to the character?", "question", buttons=1)
        if result == QMessageBox.Ok:
            print("User clicked OK")
            #check if the talent selected exceeds the number of available talent slots
            min = self.number_of_contacts["min"]
            max = self.number_of_contacts["max"]
            print(f"contact min={min}/max={max}")
            selected_contact_text = selected_contact.text()
            self.contacts_listbox.addItem(selected_contact_text)
            current_num_contacts = self.contacts_listbox.count()
            #if min contacts have been reached, user must buy more contacts up to the max
            if current_num_contacts == min:
                self.contacts_classes_listbox.setEnabled(False)
                self.select_contact_listbox.clear()
                self.contact2_pixmap = QPixmap(resource_path('images/uatu.jpg'))
                self.contact2_image.setPixmap(self.contact2_pixmap)
                self.contact_pixmap = QPixmap("")
                self.contact_image.setPixmap(self.contact_pixmap)
            elif current_num_contacts == max:
                self.contacts_classes_listbox.setEnabled(False)
                self.buy_contact_button.setEnabled(False)
                self.contact2_pixmap = QPixmap(resource_path('images/uatu.jpg'))
                self.contact2_image.setPixmap(self.contact2_pixmap)
                self.contact_pixmap = QPixmap("")
                self.contact_image.setPixmap(self.contact_pixmap)
            else:
                self.contacts_classes_listbox.setFocus()
                self.contact_pixmap = QPixmap(resource_path('images/dr_strange.jpg'))
                self.contact_image.setPixmap(self.contact_pixmap)
        elif result == QMessageBox.Cancel:
            print("User clicked Cancel")



    def contact_list_selected(self, selected_contact):
        #confirm removal of selected Talent
        if selected_contact.flags() & Qt.ItemIsEnabled:
            result = self.display_message(resource_path('images/question.jpg'), "Confirm Removing Contact", "Are you sure you want to remove this contact", "question", buttons=1)
            if result == QMessageBox.Ok:
                print("User clicked OK")
                #refund a contact slot
                min = self.number_of_contacts["min"]
                max = self.number_of_contacts["max"]
                print(f"Number of contacts - min={min} / max={max}")
                contact_text = selected_contact.text()
                print(f"contact_item={selected_contact} / contact_text={contact_text}")
                min -= 1
                self.number_of_contacts["min"] = min
                self.num_contacts_label.setText(f"Min: {min} / Max: {max}")
                contact = self.contacts_listbox.currentRow()
                self.contacts_listbox.takeItem(contact)
            elif result == QMessageBox.Cancel:
                print("User clicked Cancel")


    
    def buy_contact(self):
        #first check if there are enough resources and reduce resources by one 
        #rank or if buying a contact will exceed the maximum number of contacts
        #and display the new rank and score on the Abilities tab
        print("Buying Contact!")
        print(f"resource_rank={self.resources_rank}")
        current_resources = self.resources_rank
        new_resources = current_resources - 1
        num_contacts = self.contacts_listbox.count()
        min = self.number_of_contacts["min"]
        max = self.number_of_contacts["max"]
        print(f"contact min={min}/max={max}")
        print(f"current_resources={current_resources}, new_resources={new_resources}")
        if new_resources < 0:
            print("Not enough resources!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Resources!", "You do not have enough Resources to purchase another contact!", "warning", buttons=0)
        elif num_contacts == max or min == max:
            print("Not enough contact slots!")
            self.display_message(resource_path('images/oops.jpg'), "Not Enough Contact Slots!", "You do not have enough Contact slots to purchase another contact!", "warning", buttons=0)
        else:
            new_rank = self.ranks[new_resources]
            resources_text = self.secondary_ability_inputs["resources"]["rank"]
            resources_score_text = self.secondary_ability_inputs["resources"]["score"]
            resources_text.setText(new_rank)
            if self.std_rank_scores == 0:
                #minimum rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][0]))
            else:
                #standard rank scores
                resources_score_text.setText(str(self.rank_scores[new_rank][1]))
            
            #roll an additional talent class and add it to the list
            print("Adding Contact!")
            min +=1
            self.contact_bought += 1
            self.resources_rank -= 1
            self.number_of_contacts["min"] = min
            print(f"contact min={min}/max={max}")
            if self.number_of_contacts["min"] > 0:
                self.contacts_classes_listbox.setEnabled(True)
            self.num_contacts_label.setText(f"Min: {min} / Max: {max}")
            print(f"resources_rank={self.resources_rank}")
            print(f"self.contact_bought={self.contact_bought}")



    def save_button_clicked(self):
        print(f"Saving File!")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save to File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            #determine which radion button is checked
            if self.secret_radio.isChecked():
                secret = "(Secret)"
                public = " "
            elif self.public_radio.isChecked():
                secret = " "
                public = "(Public)"
            else:
                secret = " "
                public = " "

            #get the physical form and any optional or compound/changeling forms
            physical_form = self.physical_form_list.currentItem()
            physical_form_name = physical_form.text()
            print(f"physical_form_name={physical_form_name}")
            if physical_form_name == "Compound":
                physical_form_name = "Compound Form: "
                num = self.compound_forms
                for index in reversed(range(num)):
                    form = self.compound_form_list[index]
                    print(f"form={form}")
                    print(f"physical_form_name={physical_form_name}")
                    compound_index = self.compound_form_list.index(form)
                    print(f"compound_index={compound_index}")
                    option_form = self.compound_form_options_list[compound_index]
                    print(f"option_form={option_form}")
                    if option_form != "":
                        print(f"option_form!=''")
                        physical_form_name = physical_form_name + f"{form} "
                        if index == 0:
                            physical_form_name = physical_form_name + f"({option_form})"
                        else:
                            physical_form_name = physical_form_name + f"({option_form}), "
                    elif index == 0:
                        physical_form_name = physical_form_name + f"{form}"
                    else:
                        physical_form_name = physical_form_name + f"{form}, "
            elif self.options_list.count() > 0:
                item = self.options_list.currentItem()
                item_text = item.text()
                physical_form_name = f"{physical_form_name} ({item_text})"
            print(f"physical_form_name={physical_form_name}")
            print(f"Physical Form={physical_form}")

            try:
                with open(file_path, "w") as file:
                    file.write(f"NAME: {self.name_textbox.text()}\n")
                    file.write(f"IDENTITY: {self.identity_textbox.text()}   {secret}{public}\n")
                    file.write(f"SEX: {self.sex_combobox.currentText()}     AGE: {self.age_textbox.text()}\n")
                    file.write(f"GROUP AFFILIATION: {self.group_textbox.text()}     BASE OF OPERATOINS: {self.base_textbox.text()}\n\n")
                    file.write(f"PHYSICAL FORM: {physical_form_name}\nORIGIN OF POWER: {self.origin_textbox.text()}\n")
                    file.write(f"Bonuses: {self.bonuses_textbox.toPlainText()}\n")
                    file.write(f"Penalties: {self.penalties_textbox.toPlainText()}\n")
                    file.write(f"Weakneses: {self.weakness_textbox.toPlainText()}\n")
                    file.write(f"Notes: {self.notes_textbox.toPlainText()}\n\n\n")
                    file.write(f"ATTRIBUTES:\n")
                    for ability in self.ability_inputs:
                        rank_textbox = self.ability_inputs[ability]["rank"]
                        score_textbox = self.ability_inputs[ability]["score"]
                        rank = rank_textbox.text()
                        score = score_textbox.text()
                        file.write(f"{ability.capitalize()}: {rank} ({score})\n")
                    file.write(f"\nHealth: {self.health}     Karma: {self.karma}     ")
                    for ability in self.secondary_ability_inputs:
                        if ability != "":
                            rank_textbox = self.secondary_ability_inputs[ability]["rank"]
                            score_textbox = self.secondary_ability_inputs[ability]["score"]
                            rank = rank_textbox.text()
                            score = score_textbox.text()
                            file.write(f"{ability.capitalize()}: {rank} ({score})     ")
                    file.write(f"\n\n\nPOWERS:\n")
                    for power in self.powers_listbox.findItems("", Qt.MatchContains):
                        text = power.text()
                        file.write(f"{text}\n")
                    file.write(f"\n\nTALENTS:\n")
                    for talent in self.talents_listbox.findItems("", Qt.MatchContains):
                        text = talent.text()
                        file.write(f"{text}\n")
                    file.write(f"\n\nCONTACTS:\n")
                    for contact in self.contacts_listbox.findItems("", Qt.MatchContains):
                        text = contact.text()
                        file.write(f"{text}\n")

                QMessageBox.information(self, "Success", "File saved successfully!")
            except IOError:
                 QMessageBox.critical(self, "Error", "An error occurred while saving the file.")



    def exit_button_clicked(self):
        result = self.display_message(resource_path('images/question.jpg'), "Confirm Exit", "Are you sure you want to exit?", "question", buttons=1)
        if result == QMessageBox.Ok:
            QApplication.instance().quit()




################### BACKEND FUNTIONS ###################
    def ability_roll(self,table,roll):
        print(f"Rolling Ability or Power Rank - roll={roll}; table={table}")
        self.table_text_box.setText(f"Table {table}")
        if table == 1:
            if roll < 6:
                power_rank_index = 1
            elif roll < 11:
                power_rank_index = 2
            elif roll < 21:
                power_rank_index = 3
            elif roll < 41:
                power_rank_index = 4
            elif roll < 61:
                power_rank_index = 5
            elif roll < 81:
                power_rank_index = 6
            elif roll < 97:
                power_rank_index = 7
            else:
                power_rank_index = 8

        if table == 2:
            if roll < 6:
                power_rank_index = 1
            elif roll < 26:
                power_rank_index = 2
            elif roll < 78:
                power_rank_index = 3
            elif roll < 96:
                power_rank_index = 4
            else:
                power_rank_index = 5

        if table == 3:
            if roll < 6:
                power_rank_index = 1
            elif roll < 11:
                power_rank_index = 2
            elif roll < 41:
                power_rank_index = 3
            elif roll < 81:
                power_rank_index = 4
            elif roll < 96:
                power_rank_index = 5
            else:
                power_rank_index = 6

        if table == 4:
            if roll < 6:
                power_rank_index = 1
            elif roll < 11:
                power_rank_index = 2
            elif roll < 16:
                power_rank_index = 3
            elif roll < 41:
                power_rank_index = 4
            elif roll < 51:
                power_rank_index = 5
            elif roll < 71:
                power_rank_index = 6
            elif roll < 91:
                power_rank_index = 7
            elif roll < 99:
                power_rank_index = 8
            else:
                power_rank_index = 9
        
        if table == 5:
            if roll < 11:
                power_rank_index = 1
            elif roll < 21:
                power_rank_index = 2
            elif roll < 31:
                power_rank_index = 3
            elif roll < 41:
                power_rank_index = 4
            elif roll < 61:
                power_rank_index = 5
            elif roll < 71:
                power_rank_index = 6
            elif roll < 81:
                power_rank_index = 7
            elif roll < 96:
                power_rank_index = 8
            else:
                power_rank_index = 9

        return power_rank_index
    


    #clear attributes
    def clear_info(self):
        self.fighting_bonus = 0
        self.agility_bonus = 0
        self.strength_bonus = 0
        self.endurance_bonus = 0
        self.reason_bonus = 0
        self.intuition_bonus = 0
        self.psyche_bonus = 0
        self.resources_bonus = 0
        self.popularity_bonus = 0
        #resource/popularity_rank is used to make adding and subtracting 
        #calculations using the current rank
        self.resources_rank = -1
        self.popularity_rank = -1
        #pf_resources/popularity is used to determine ability set by physical form
        self.pf_resources_rank = -1
        self.pf_popularity_rank = -1
        #original_resources is used to easily reset Resources back to original 
        #if powers were purchased
        self.original_resources_rank = -1
        self.ability_bonus = 0
        self.health = 0
        self.karma = 0
        self.health_multiplier = 1
        self.power_bonus = 0
        self.initial_contacts = -1
        self.compound_forms = 0
        self.current_compound_form_index = 0
        self.current_compound_form = ""
        self.compound_form_list = ["","","","",""]
        self.compound_form_options_list = ["","","","",""]
        self.std_rank_scores = 0
        self.ability_bonus_button_was_clicked = 0
        self.power_rank_above_remarkable = 0
        self.number_of_powers = {"min": 0, "max": 0}
        self.number_of_talents = {"min": 0, "max": 0}
        self.number_of_contacts = {"min": 0, "max": 0}
        self.purchased_powers = []
        self.talent_bought = 0
        self.contact_bought = 0
        self.animal_detection = 0
        self.energy_form = 0
        self.deity_travel_power = 0
        self.wings_travel_power = 0



    #toggle Standard Rank Scores on and off
    def toggle_std_rank(self):
        print("Toggling Minimum/Standard ranks scores...")
        checked = self.std_rank_scores_action.isChecked()
        self.health = 0
        self.karma = 0

        if checked:#using standard rank scores
            self.std_rank_scores = 1
            self.update_rank_scores(1)

        else:#using minimun rank scores
            self.std_rank_scores = 0
            self.update_rank_scores(0)

        self.health = self.health * self.health_multiplier
        self.health_textbox.setText(str(self.health))
        self.karma_textbox.setText(str(self.karma))



    def update_rank_scores(self, index):
        #update the score boxes and Health and Karma totals on the Abilities tab
        for ability, inputs in self.ability_inputs.items():
            rank_textbox = self.ability_inputs[ability]["rank"]
            rank_name = rank_textbox.text()
            if ability in {"fighting", "agility", "strength", "endurance"}:
                self.health += self.rank_scores[rank_name][index]
            elif ability in {"reason", "intuition", "psyche"}:
                self.karma += self.rank_scores[rank_name][index]
            inputs["score"].setText(str(self.rank_scores[rank_name][index]))
        for ability, inputs in self.secondary_ability_inputs.items():
            rank_textbox = self.secondary_ability_inputs[ability]["rank"]
            rank_name = rank_textbox.text()
            inputs["score"].setText(str(self.rank_scores[rank_name][index]))
        #update the power list
        for power in self.powers_listbox.findItems("", Qt.MatchContains):
            #split words in the power(power - power rank (score))
            text = power.text()
            words = text.split(" ")
            print(f"text={text}, words={words}")
            for i, word in enumerate(words):
                if "(" in word:
                    print(f"word has parentheses={word}")
                    score_index = i
            #iterate through each word
            for word in words:
                #if the word is a rank name
                if word in self.ranks:
                    #get the appropriate score based on the rank name
                    power_rank_score = (str(self.rank_scores[word][index]))
                    #update the rank score in the list to the new score and 
                    #update the power item in the power list
                    #Energy Emission powers have more words with the emission 
                    #point and should add the semicolon back
                    if "emitted" in words:
                        words[score_index] = f"({power_rank_score});"
                    else:
                        words[score_index] = f"({power_rank_score})"
                    power.setText(f"{' '.join(words)}")



    def fill_roll_textboxes(self, abilities, table):
        #roll randomly for each ability then display the roll, rank and bonus
        #for each ability in the Table column
        print("*************fill_roll_textboxes*************")
        print(f"resource_rank={self.resources_rank}")
        for ability, inputs in abilities:
            print(f"ability={ability}, inputs={inputs}")
            #randomly roll for each ability on the given table
            roll = randint(1,100)
            rankindex = self.ability_roll(table,roll)
            inputs["roll"].setText(str(roll))
            inputs["rank_roll"].setText(f"{self.ranks[rankindex]}")

            #get the ability bonus and add it to the bonus field
            if ability:
                bonus = getattr(self, f"{ability}_bonus")
            print(f"bonus={bonus}")
            if bonus > 0:
                inputs["bonus"].setText(f"+{str(bonus)}")
            else:
                inputs["bonus"].setText(str(bonus))
            #add the bonus to the rank
            rankindex += bonus
            if rankindex < 1:#If rolled rank is Feeble do not lower below Feeble
                rankindex = 1
            print(f"rankindex={rankindex}")

            #check if Resources or Popularity was set by the Physical Form else
            #apply the randomly rolled rank for each primary/secondary ability
            if self.pf_resources_rank > -1:
                print(f"pf_resources_rank>-1")
                if ability == "resources":
                    print(f"ability=resources")
                    rankindex = self.pf_resources_rank
                    self.resources_rank = self.pf_resources_rank
                    self.original_resources_rank = self.pf_resources_rank
            else: #set the resource or popularity rank attribute to the rolled one
                if ability == "resources":
                    self.resources_rank = rankindex
                    self.original_resources_rank = rankindex
            
            if self.pf_popularity_rank > -1:
                print(f"pf_popularity_rank>-1")
                if ability == "popularity":
                    print(f"ability=resources")
                    rankindex = self.pf_popularity_rank
                    self.popularity_rank = self.pf_popularity_rank
            else: #set the resource or popularity rank attribute to the rolled one
                if ability == "popularity":
                    self.popularity_rank = rankindex
            print(f"resource_rank={self.resources_rank}")

            rank_name = self.ranks[rankindex]
            inputs["rank"].setText(f"{rank_name}")
            print(f"rank_name={rank_name}")
            if self.std_rank_scores == 0:
                #minimum rank scores
                score1 = self.rank_scores[rank_name][0]
                score2 = str(self.rank_scores[rank_name][0])
                print(f"score1={score1}, score2={score2}")
                inputs["score"].setText(str(self.rank_scores[rank_name][0]))
                if ability in {"fighting", "agility", "strength", "endurance"}:
                    self.health += self.rank_scores[rank_name][0]
                elif ability in {"reason", "intuition", "psyche"}:
                    self.karma += self.rank_scores[rank_name][0]
            else:
                #standard rank scores
                inputs["score"].setText(str(self.rank_scores[rank_name][1]))
                if ability in {"fighting", "agility", "strength", "endurance"}:
                    self.health += self.rank_scores[rank_name][1]
                elif ability in {"reason", "intuition", "psyche"}:
                    self.karma += self.rank_scores[rank_name][1]



    def roll_number_powers(self, type):
        roll = randint(1,100)
        print(f"roll_number_powers roll={roll}, type={type}")
        # Define ranges and corresponding values for each type
        ranges = [
            (13, {"powers": {"min": 1, "max": 3}, "talents": {"min": 0, "max": 3}, "contacts": {"min": 0, "max": 2}}),
            (27, {"powers": {"min": 2, "max": 4}, "talents": {"min": 1, "max": 4}, "contacts": {"min": 0, "max": 4}}),
            (42, {"powers": {"min": 3, "max": 5}, "talents": {"min": 1, "max": 6}, "contacts": {"min": 1, "max": 4}}),
            (56, {"powers": {"min": 4, "max": 6}, "talents": {"min": 2, "max": 4}, "contacts": {"min": 2, "max": 4}}),
            (67, {"powers": {"min": 5, "max": 7}, "talents": {"min": 2, "max": 6}, "contacts": {"min": 2, "max": 6}}),
            (76, {"powers": {"min": 6, "max": 8}, "talents": {"min": 2, "max": 8}, "contacts": {"min": 3, "max": 3}}),
            (84, {"powers": {"min": 7, "max": 9}, "talents": {"min": 3, "max": 4}, "contacts": {"min": 3, "max": 4}}),
            (90, {"powers": {"min": 8, "max": 10}, "talents": {"min": 3, "max": 6}, "contacts": {"min": 3, "max": 6}}),
            (95, {"powers": {"min": 9, "max": 12}, "talents": {"min": 4, "max": 4}, "contacts": {"min": 4, "max": 4}}),
            (98, {"powers": {"min": 10, "max": 12}, "talents": {"min": 4, "max": 8}, "contacts": {"min": 4, "max": 5}}),
            (100, {"powers": {"min": 12, "max": 14}, "talents": {"min": 5, "max": 6}, "contacts": {"min": 5, "max": 5}}),
            (101, {"powers": {"min": 14, "max": 18}, "talents": {"min": 6, "max": 8}, "contacts": {"min": 6, "max": 6}})
        ]

        # Find the appropriate range and set the values
        for threshold, values in ranges:
            if roll < threshold:
                setattr(self, f"number_of_{type}", values[type])
                break
            
        #apply any number of powers bonuses/penalties
        if type == "powers":
            if self.number_of_powers["min"] == 1 and self.power_bonus == -1:
                self.number_of_powers["min"] = 1
            else:
                self.number_of_powers["min"] += self.power_bonus
        elif type == "contacts":
            if self.initial_contacts == 0: #0 initial contants
                self.number_of_contacts["min"] = 0
            elif self.initial_contacts > 2:#at least one initial contant
                if self.number_of_contacts["min"] == 0:
                    self.number_of_contacts["min"] = 1
                elif self.number_of_contacts["min"] == 1:
                    self.contacts_classes_listbox.setEnabled(False)
            elif self.initial_contacts == 1:#only one initial contact
                if self.number_of_contacts["min"] == 0:
                    self.number_of_contacts["min"] = 1
                else:
                    self.number_of_contacts["min"] = 1
                self.contacts_classes_listbox.setEnabled(False)

                

    def roll_power_class(self):
        roll = randint(1,100)
        print(f"Roll Power Classes roll={roll}")
        if roll < 6:
             power_class = "Defensive"
        elif roll < 12:
            power_class = "Detection"
        elif roll < 17:
            power_class = "Energy Control"
        elif roll < 25:
            power_class = "Energy Emission"
        elif roll < 30:
            power_class = "Fighting"
        elif roll < 32:
            power_class = "Illusory"
        elif roll < 36:
            power_class = "Lifeform Control"
        elif roll < 41:
            power_class = "Magical"
        elif roll < 48:
            power_class = "Matter Control"
        elif roll < 54:
            power_class = "Matter Conversion"
        elif roll < 58:
            power_class = "Matter Creation"
        elif roll < 72:
            power_class = "Mental Enhancement"
        elif roll < 86:
            power_class = "Physical Enhancement"
        elif roll < 89:
            power_class = "Power Control"
        elif roll < 93:
            power_class = "Self-Alteration"
        else:
            power_class = "Travel"
        return power_class



    def energy_emission_body_part(self):
        roll = randint(1,100)
        if roll < 15:
            epoint = "Entire body"
        elif roll < 23:
            epoint = "Head"
        elif roll < 31:
            epoint = "Eyes"
        elif roll < 39:
            epoint = "Mouth and nose"
        elif roll < 47:
            epoint = "Torso"
        elif roll < 55:
            epoint = "Arms"
        elif roll < 63:
            epoint = "Hands"
        elif roll < 68:
            epoint = "Fingers"
        elif roll < 71:
            epoint = "Legs"
        elif roll < 74:
            epoint = "Feet"
        elif roll < 77:
            epoint = "Wings"
        elif roll < 82:
            epoint = "Antennae/horns"
        elif roll < 87:
            epoint = "Tail"
        elif roll <= 100:
            epoint = "Any location"
        return epoint



    def roll_talent_class(self):
        roll = randint(1,100)
        print(f"Roll Talent Classes roll={roll}")
        if roll < 21:
            self.talent_classes_listbox.addItem("Weapon Skills")
        elif roll < 46:
            self.talent_classes_listbox.addItem("Fighting Skills")
        elif roll < 66:
            self.talent_classes_listbox.addItem("Professional Skills")
        elif roll < 86:
            self.talent_classes_listbox.addItem("Scientific Skills")
        elif roll < 91:
            self.talent_classes_listbox.addItem("Mystical and Mental Skills")
        elif roll <= 100:
            self.talent_classes_listbox.addItem("Other Skills")



    def display_message(self, icon, title, text, type, buttons=0):
        msg = QMessageBox()
        font = QFont("Comic Sans MS", 12)
        msg.setFont(font)
        msg.setWindowIcon(QIcon(icon))
        msg.setWindowTitle(title)
        msg.setText(text)
        if type == "warning":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Question)
        if buttons:
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            return msg.exec_()
        else:
            msg.exec_()



    def min_std_rank_score(self, rank):
        if self.std_rank_scores == 0:
            #minimum rank scores
            score = self.rank_scores[rank][0]
        else:
            #standard rank scores
            score = self.rank_scores[rank][1]
        return score



    def biophysical_random_option(self):
        roll = randint(1,100)
        if roll < 25:
            text = 'Healing'
        elif roll < 45:
            text = 'Regeneration'
        elif roll < 49:
            text = 'Revival'
        elif roll < 69:
            text = 'Damage Transferral'
        elif roll < 77:
            text = 'Decay'
        elif roll < 93:
            text = 'Disruption'
        elif roll <= 100:
            text = 'Aging'
        return text
    


    def show_instructions(self):
        instructions_dialog = QDialog()
        instructions_dialog.setWindowIcon(QIcon(resource_path('images/mshJudge.jpg')))
        instructions_dialog.setWindowTitle("Instructions")
        instructions_dialog.resize(700, 800)
        instructions_label = QLabel("""MSH Character Generator 		.v 2.00.00			By TaskmasterX


The MSH Character Generator, or MSHCG for short, is designed to allow players of the classic Marvel Superheroes RPG by TSR to create new characters as quickly as possible using virtually the same method as described in the Ultimate Powers Book and Players Handbook of the RPGs. This program is not meant to replace the UPB, rather it is meant to be used with the UPB. You still need the rulebooks and UPB for the Power descriptions and other useful information that is not provided by this program. The rulebooks and UPB can be found on the internet with a Google search. Also, this is not meant to completely generate a new character. This program essentially provides a quick and easy way to create the foundation, or structure, for the character that you then flesh-out after the character sheet has been saved.

If you have any questions or comments, email me at taskmasterxff@yahoo.com



INSTRUCTIONS
                                    
Physical Form Tab
Choose a physical form from the list in the Physical Form list. You can use the [Random] button to allow the program to “roll” (randomly determine) the physical form for you. Once a physical form is selected, all bonuses, penalties and weaknesses associated with that form will appear in the appropriate boxes. 

The Origin of Power is also randomly determined and displayed in the Origin of Power box. Each time you select a physical form, the origin of power is recalculated, even if you select the same form.  

Some forms require more selections before you can move on. Select the necessary options in the Physical Form Options or the Changeling/Compound Form boxes to continue to the next tab, Abilities.


Abilities Tab
The Abilities tab is where you roll for your FASERIP stats as well as for Resources and Popularity. Click the [Roll Abilities] button to roll for all the abilities at once. Health and Karma are automatically calculated, and any bonuses/penalties associated with the physical form are applied. You can keep clicking on the [Roll Abilities] button to re-roll the stats. 

If the physical form allows you to increase any ability +1 CS, then use the [+] buttons next to the ability you want to raise. Once you are finished here click on the Powers tab.


Powers Tab
Click the [Roll Power Classes] button to determine your minimum and maximum power slots and the Power Classes that fill your minimum number of slots. You can re-roll by repeatedly clicking the button.

Once the number of powers and the Power Classes have been determined, you can then purchase more minimum power slots with Resource Ranks. Use the [ $ Buy Power ] button to purchase another power slot for two Resource ranks. 

Click on one of the Power Classes in the list and then click the [ Roll Power ] button to roll for a power in that class. You can repeatedly click the button to re-roll the power for that class. Any bonus or optional powers that go along with that power are listed in the appropriate boxes. Once the power you want appears in the Power: box, you can confirm that you want to add that power to the character by clicking the [Add Power(s)] button. When you add the power, it rolls the Power Rank for that power and adds it to the Powers List.

If any bonus powers are listed, you must select one before you can add the power. You can also choose optional powers before clicking the [Add Power(s)] button so that the optional power is added as well. Some Powers have another Power Class as an optional Power. Selecting a Power Class as an optional Power will add that Power class to the Power Classes list.

You can remove Power Classes by using the [ X Remove Power ] button. You will most likely use this if you choose Powers that use more than one slot or choose Bonus or Optional Powers that end up filling your maximum Power slots, and you can’t add any more. You can delete Power Classes that you don’t need so that you can continue by clicking on the [Generate Weakness] button.

Once all the powers have been added, the [Generate Weakness] button will become active. Click this button to generate a weakness as described in the UPB. You must generate a weakness before continuing to the next tab.


Talents Tab
The Talents tab is similar to the Powers tab. The [Roll Talents] button will randomly determine the minimum and maximum Talent slots and which Talent Classes the character has. 

You can purchase Talents with Resources, just like you can purchase Powers. One talent costs one Resource rank.

Click the Talent Class in the list to either delete it with the [ X Remove Talent ] button, or roll for a Talent within that class with the [ Roll Talent ] button.

Select the Talent in the box to add it to the character’s list of Talents. Once all the Talents have been determined, click the Contacts tab.


Contacts Tab
This tab works very much like the Talents tab. Click the [Roll Contacts] button to determine the minimum and maximum slots for Contacts. You can purchase more Contact slots with Resource ranks (one Contact slot for one Resource rank). Then click one of the Contact Classes to display all the types of Contacts for that Class. Click the Contact to add it to the Contacts: list.


Last Steps
If the physical form has multiple forms that require you to roll different Abilities and/or Powers for each form, save the file for the first form and roll the Abilities and/or Powers for the next form and then save it as a separate file. Once all the forms are complete you can copy and paste the text from all files into one file.
                                    
The last thing you should do is give the character a name, identity (secret or public), age, sex and any group affiliations or base of operations. You can then save the character in a text file on your computer. Click the [Save] button and the program will prompt you to provide the path and filename for the character sheet.


Options
You can toggle the Use Standard Rank Scores option to use the standard scores for each rank rather than the minimum.

-TaskmasterX
taskmasterxff@yahoo.com
                                    """)
        instructions_label.setFont(QFont('Arial', 12))
        instructions_label.setWordWrap(True)
        instructions_label.resize(700, 800)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(instructions_label)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        instructions_dialog.setLayout(layout)
        instructions_dialog.exec_()



    def show_about(self):
        about_dialog = QDialog()
        about_dialog.setFont(QFont('Gil Sans', 20))
        about_dialog.setWindowIcon(QIcon(resource_path('images/mshPlayer.jpg')))
        about_dialog.setWindowTitle("About MSH Character Generator")
        about_dialog.resize(650, 320)

        #add the image
        pixmap = QPixmap(resource_path('images/mshPlayer.jpg'))
        about_image = QLabel()
        about_image.setPixmap(pixmap)
        about_image.setAlignment(Qt.AlignLeft)
        about_image.setFixedSize(200, 300)
        about_image.setScaledContents(True)

        # Add text labels
        title_label = QLabel("MSH Character Generator\n")
        title_label.setFont(QFont('Arial', 12))
        title_label.setStyleSheet("color: black; font-size: 12px; background-color: rgba(0, 0, 0, 0);")

        # Version and copyright label
        version_label = QLabel("Version 2.0.0.0\n\nCopyright © 2025")
        version_label.setFont(QFont('Arial', 12))
        version_label.setStyleSheet("color: black; font-size: 12px; background-color: rgba(0, 0, 0, 0);")

        # Author information
        author_label = QLabel("\n\nTaskmasterX\n")
        author_label.setFont(QFont('Arial', 12))
        author_label.setStyleSheet("color: black; font-size: 12px; background-color: rgba(0, 0, 0, 0);")

        # Information label
        info_label = QTextEdit(
        """Creates characters for the classic Marvel Super Heroes RPG by TSR.
        This software is freeware.   Images are the property of Marvel Comics 
        and TSR.
        Contact: taskmasterxff@yahoo.com"""
        )
        info_label.setFont(QFont('Arial', 12))
        info_label.setStyleSheet("color: black; font-size: 12px; background-color: rgba(0, 0, 0, 0);")

        # OK button to close the dialog
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(70, 35)
        ok_button.setStyleSheet("color: black; font-size: 14px;")
        ok_button.clicked.connect(about_dialog.accept)

        # Layout setup
        layout = QHBoxLayout()
        info_layout = QVBoxLayout()

        info_layout.addWidget(title_label)
        info_layout.addWidget(version_label)
        info_layout.addWidget(author_label)
        info_layout.addWidget(info_label)
        info_layout.addWidget(ok_button, alignment=Qt.AlignRight)

        layout.addWidget(about_image)
        layout.addLayout(info_layout)
        about_dialog.setLayout(layout)

        # Show as a modal dialog
        about_dialog.exec_()





class BiophysicalOptionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Biophysical Control Type")
        self.layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.addItems(["Healing", "Regeneration", "Revival", 
                                   "Damage Transferral", "Decay", "Disruption", 
                                   "Aging", "Random"])
        self.layout.addWidget(self.list_widget)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def get_selected_option(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None



#show splashscreen
def show_splash():
    app = QApplication(sys.argv)

    # Load splash image
    pixmap = QPixmap(resource_path('images/UPB_sm.jpg'))
    
    # Create QLabel for splash screen
    splash = QLabel()
    splash.setPixmap(pixmap)
    splash.setAlignment(Qt.AlignLeft)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.resize(500, 270)

    # Add text labels
    title_label = QLabel("MSH Character Generator", splash)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setGeometry(213, 50, 283, 100)
    title_label.setStyleSheet("color: black; font-size: 24px; background-color: rgba(0, 0, 0, 0);")
    title_label.setFont(QFont('Gil Sans', 20))
    version_label = QLabel("Version 2.0\n\nCopyright ©  2025", splash)
    version_label.setAlignment(Qt.AlignCenter)
    version_label.setGeometry(213, 150, 283, 100)
    version_label.setStyleSheet("color: black; font-size: 12px; background-color: rgba(0, 0, 0, 0);")
    version_label.setFont(QFont('Arial', 20))

    # Show splash screen
    splash.show()

    # Close splash and open main window after 3 seconds
    QTimer.singleShot(3000, lambda: (splash.close(), show_main_window()))

    sys.exit(app.exec_())



# Show main window
def show_main_window():
    window= MainWindow()
    window.show()



def resource_path(relative_path):
    #Get absolute path to resource, works for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



if __name__ == "__main__":
    show_splash()



