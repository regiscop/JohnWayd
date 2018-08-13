# Feel free to modify the code. THIS IS A CHATBOT OPEN TO COLLABORATION. You can modify the script of this chatbot freely
# Once a week, the code is pushed in production
# Wanna build your own bot? we can host and run it for free if you use this scripting method and you make it public: apply to regiscop@gmail.com
# Use BOTSAY to send a message to a user
# Use USER to use the object USER in an INTERACTION
# Use STATE to change the STATE of an interaction
# Use USERDICT to have access to all info related to a USER
# Use INBOX to read all unread messages
# Use CLR_INBOX to clear all unread messages
# Use INTER_CALLS to know the number of times an interactions has been called
# Use LAUNCH to launch any INTERACTION to any user





# -------------------------------------------------------------------------------------------------------------------


INTERACTION ProcessSpontaneous
    INPUT  user
        

    USEFULNESS:
        if INBOX[USER]:
            return 2.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'process'

        STATE_DEF 'process'
            if INBOX[USER] and USER.s_greeted_by_john is True:
                if INBOX[USER][-1].text == "poke":
                    # Some channels like Facebook or Telegram allow to send pictures or poke stuff; Currently pictures and non-text messages are replaced by "poke"
                    pass
                else:
                    infos = {}
                    minsize = 100
                    for msg in INBOX[USER]:
                        minsize = min(minsize, len(msg.text))
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'name'))
                        infos.update(corp_get(results, 'activity'))
                        infos.update(corp_get(results, 'ner'))
                        infos.update(corp_get(results, 'gettrained'))
                        infos.update(corp_get(results, 'help'))
                        infos.update(corp_get(results, 'sentiment'))
                        infos.update(corp_get(results, 'gdpr'))
                        infos.update(corp_get(results, 'tone'))
                        if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                            int = AskLocation(BOT, USER)
                            int.state = 'wait for answer'
                            int.time_asked = datetime.now()
                            LAUNCH_INTERACTION(int)
                            STATE = 'success'
                            return

                    if 'tone' in infos:
                        if infos['tone'] == 'rude' and infos['tone_score'] > 0.6:
                            BOTSAY(USER, lingua.dont_be_so_rude())
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'gdpr' in infos:
                        if infos['gdpr'] == 'true' and infos['gdpr_score'] > 0.8:
                            BOTSAY(USER, "We will delete all data related to you")
                            CLR_INBOX(USER)
                            del USER
                            return
                            STATE = 'success'
                            return

                    if 'ner' in infos:
                        if infos['ner'] == 'true' and infos['ner_score'] > 0.5:
                            BOTSAY(USER, "My dear, I'm sorry but you are not currently attached to a run. Please wait til I suggest you another NeverEndingRun...")
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'gettrained' in infos:
                        if infos['gettrained'] == 'true' and infos['gettrained_score'] > 0.5:
                            if 's_home_location' not in USERDICT:
                                LAUNCH_INTERACTION(AskLocation(BOT, USER))
                            if 'like_running' not in USERDICT:
                                from .running import AskAboutRunning, AskAboutNER
                                QUERE_INTERACTION(AskAboutRunning(BOT, USER))
                            if 'like_NER' not in USERDICT:
                                from .running import AskAboutRunning, AskAboutNER
                                ADD_POSSIBLE(AskAboutNER(BOT, USER))
                            if 's_home_location' in USERDICT and 'like_running' in USERDICT:
                                BOTSAY(USER, "I'll ask to other participants in your area who is willing to run with you. I'll keep you posted asap. But keep in mind that the WAYD organization declines all responsibilities on the runs organized via this Chatting Robot.")
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'help' in infos:
                        if infos['help'] == 'true' and infos['help_score'] > 0.8:
                            BOTSAY(USER, "You can give me your location by using the 'Share a location' functionality of your app and I'll find in your area who is willing to run this week... :-) ")
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'tone' in infos:
                        if infos['tone'] == 'stopspamming' and infos['tone_score'] > 0.8:
                            BOTSAY(USER, lingua.ok())
                            CLR_INBOX(USER)
                            # This will have a direct effect on the Silent interaction
                            USER.s_time_of_last_message = str(datetime.now() - timedelta(hours=48))
                            STATE = 'success'
                            return

                    if 'name' in infos:
                        if infos['name_score'] > 0.99 and minsize > 100:  # 0.4 to too much, do not even recognize "My name is Bob"
                            int = AskName(BOT, USER)
                            int.state = 'wait for answer'
                            int.time_asked = datetime.now()
                            LAUNCH_INTERACTION(int)
                            STATE = 'success'
                            return

                    answer = sa.is_general_question(INBOX[USER][-1].text)
                    if answer:
                        BOTSAY(USER, answer.replace("julia", "john").replace("Julia", "John").replace("JuliaWayd","JohnWayd"))
                    else:
                        BOTSAY(USER, lingua.i_dont_understand_john())

            elif INBOX[USER] and USER.s_greeted_by_john is not True:
                QUERE_INTERACTION(WelcomeNewUser(BOT, USER))
            CLR_INBOX(USER)
            STATE = 'success'

        STATE_DEF 'success'
            if USER.s_greeted_by_john is True:
                LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'
            RESETTING_INTERACTION

        STATE_DEF 'end'
            pass
# -------------------------------------------------------------------------------------------------------------------


INTERACTION WelcomeNewUser
    INPUT  user

    USEFULNESS:
        if USER.s_greeted_by_john:
            return 0.0
        else:
            return 3.0

    EXECUTE:

        START_STATE
            STATE = 'greet'

        STATE_DEF 'greet'
            BOTSAY(USER, "Hi, I'm John Wayd! The organizer of the Never Ending Run in your neighbourhood! I'm an opensource chatbot.")
            USER.s_greeted_by_john = True
            USER.greeted_date = datetime.now()
            CLR_INBOX(USER)

            if USER.last_channel_per_bot[BOT.name] == "Facebook":
                try:
                    r = requests.get("https://graph.facebook.com/v2.8/"+ USER.s_numbers['Facebook'] +"?fields=first_name,last_name,gender,timezone&access_token=wdfsdf")
                    try:
                        USER.gender = r.json()['gender']
                    except:
                        USER.gender = None
                    USER.s_name = r.json()['first_name']
                    USER.s_last_name = r.json()['last_name']
                except:
                    USER.gender = 'male'
                    USER.s_name = 'Mister X'
            elif USER.last_channel_per_bot[BOT.name] == "Twilio":
                USER.gender = 'male'
                USER.s_name = 'Mister X'
            else:
                ADD_POSSIBLE(AskName(BOT, USER))
            STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION AskName
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if USER.s_name:
            return 0.0
        elif not LAUNCHES:
            # We don't know the name and this interaction never ran before
            return 0.5
        elif TIME_SINCE_LAST_CALL < 60*10.0:
            # We still don't know the name but apparently we already asked without success
            return 0.0
        else:
            return 0.5

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:  # because we have to go thru the state "None" before
                BOTSAY(USER, lingua.whats_your_name())
            elif STATECALLS <= 2:  # because we have to go thru the state "Failure" "None" before
                BOTSAY(USER, "You haven't told me your name yet?")
            elif STATECALLS <= 3:
                BOTSAY(USER, "You still don't want to tell me your name?")
            elif STATECALLS <= 4:
                BOTSAY(USER, "I guess I will never get to know your name...")
                # "Do you have privacy concerns???"
            else:
                BOTSAY(USER, "As I don't know your name, I will call you Mr. Pink.")
                USER.s_name = 'Mr. Pink'
                STATE = 'success'

            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'someone'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'logic'))
                    if ' ' not in msg.text:
                        infos.update({'any': msg.text,
                                      'any_score': 1})
                    infos.update(corp_get(results, 'any'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                if 'someone' in infos and 'logic' in infos and infos['logic'] == "negative":
                    BOTSAY(USER, "haha! trying to test me? I'm smarter than you think... So... What's your name then?")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
                if 'someone' in infos or 'any' in infos:
                    answer = sa.get_gender_based_on_name(infos['someone'] if 'someone' in infos else infos['any'])
                    if (infos['someone'] if 'someone' in infos else infos['any']).lower() == "john":
                        BOTSAY(USER, "Really?'{}'!. Just like me?. Are you sure I got it right?".format(
                            infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = "John"
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            ADD_AGAIN_POSSIBLE(AskGender(BOT, USER))
                        return
                    if answer and answer['samples'] < 1000:
                        BOTSAY(USER, "Really?'{}'!. That's unusual. Are you sure I got it right?".format(infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            ADD_AGAIN_POSSIBLE(AskGender(BOT, USER))
                        return
                    elif ('someone_score' in infos and infos['someone_score'] < 0.00001) or ('any' in infos and infos['any_score'] < 0.00001):
                        BOTSAY(USER,
                                     "It's the first time I meet someone named '{}'!. Are you sure I got it right?".format(
                                         infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        return
                    USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(USER, "Nice to meet you, {}!".format(USER.s_name))
                    CLR_INBOX(USER)

                    if answer is not None and answer['accuracy'] > 95:
                        USER.gender = answer['gender']
                    elif answer is not None and answer['accuracy'] > 80:
                        if answer['gender'] == 'female':
                            BOTSAY(USER, "I know a few {} named like that, but also a {}.".format("girls", "boy"))
                        else:
                            BOTSAY(USER, "I know a few {} named like that, but also a {}.".format("boys", "girl"))
                        LAUNCH_INTERACTION(AskGender(BOT, USER))
                    else:
                        BOTSAY(USER, "mmm... I don't know any people named like that.")
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            LAUNCH_INTERACTION(AskGender(BOT, USER))
                    STATE = 'success'
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'someone'))

                if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                    BOTSAY(USER, "ok! got it! ... then,  nice to meet you, {}!".format(USER.s_name))
                    ADD_POSSIBLE(AskGender(BOT, USER))
                    CLR_INBOX(USER)
                    here = os.path.dirname(__file__)
                    file = os.path.join(here, 'first_names.txt')
                    file = file.replace('john', 'wordpresso').replace('interactions', 'data')
                    with open(file, 'a') as nf:
                        nf.write(USER.s_name + '\n')
                    STATE = 'success'
                    return
                elif 'someone' in infos and 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    USER.s_name = infos['someone']
                    BOTSAY(USER, "Ok! Understood! Nice to meet you, {}!".format(USER.s_name))
                    ADD_POSSIBLE(AskGender(BOT, USER))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    BOTSAY(USER, "Ok! What's your name then?")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
                else:
                    BOTSAY(USER, "I'm not sure I get it")
                    STATE = 'wait for confirmation'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                BOTSAY(USER, " '{}'! Did I understand your name correctly?".format(USER.s_name))
                self.time_asked = datetime.now()
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskGender
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if USER.gender:
            return 0.0
        else:
            return 0.9

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            BOTSAY(USER, "Are you male or female?")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'gender'))
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.0:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                if 'gender' in infos and infos['gender_score'] > 0.0:
                    USER.gender = infos['gender']
                    BOTSAY(USER, lingua.ok())
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------


INTERACTION AskLocation
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if 's_home_location' in USERDICT:
            # We already know!
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        else:
            try:
                return max(USER.demand_for_info['s_home_location'] / 100000.0, level_start_ask_about)
            except:
                return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if USER.last_channel_per_bot[BOT.name] in ["Telegram", "Facebook", "Line", "Viber"]:
                BOTSAY(USER, "Give me your home location so I can search for running activities around your place. Please point me the precise position of where you live with the 'share location' functionality of your app!")
            else:
                BOTSAY(USER, "Tell me where your home is located so I can search for activities around you. Give me your street address! (it's better if you give me your exact street address so I can search very close to your home)")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos

                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            BOTSAY(USER, "I didn't recognize your address, can you retype it please?")
                            CLR_INBOX(USER)
                            self.time_asked = datetime.now()
                            STATE = 'wait for answer'
                            return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER, "Ok, got it, but this is too vague for a precise search. Can you retype your street address please?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER, "Thanks a lot, {}! I did record this location as your home location. Feel free to use the 'share location' functionality any time later...".format(USER.s_name or ("Miss" if USER.gender == 'female' else "Mister")))
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait_for_answer_bis'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos
                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            results = corpus.process(msg.text)
                            infos.update(corp_get(results, 'boolean'))
                            infos.update(corp_get(results, 'tone'))
                            infos.update((corp_get(results, 'concern')))

                            if ('boolean' in infos and infos['boolean'] == False) or 'tone' in infos or 'concern' in infos:
                                BOTSAY(USER, "Ok, I guess you don't want to give you address! Let's continue the discussion anyway but just be aware that it's going to be more difficult to find something cool around you...")
                                CLR_INBOX(USER)
                                STATE = 'success'
                                return
                            else:
                                BOTSAY(USER, "I didn't recognize your address, can you retype it please?")
                                CLR_INBOX(USER)
                                self.time_asked = datetime.now()
                                STATE = 'wait_for_answer_bis'
                                return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER, "Ok, got it, but this is again too vague. Can you retype your street address?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER, lingua.thanks())
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            ADD_POSSIBLE(ReAskLocation(BOT, USER))
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION ConfirmExactLocation
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if 's_home_location' in USERDICT and 'validated' in USER.s_home_location and USER.s_home_location['validated'] is True:
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        else:
            return 1.0

    EXECUTE:

        START_STATE
            STATE = 'ask_confirmation'

        STATE_DEF 'ask_confirmation'
            BOTSAY(USER, "As you might/will host an event, I need you to confirm that your hosting address to indicate to neighbours/participants is the following:" + str(USER.s_home_location['street-address']) + ". Do you confirm? (y/n)")
            STATE = 'wait_for_confirmation'
            self.time_asked = datetime.now()

        STATE_DEF 'wait_for_confirmation'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))

                if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                    BOTSAY(USER, "Cool")
                    CLR_INBOX(USER)
                    USER.s_home_location['validated'] = True
                    STATE = 'success'
                    return
                elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    BOTSAY(USER, "Ok! Give me your exact street address!")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait_for_confirmation' and self.get_state_calls_with_msg() >= 2:
                BOTSAY(USER,"Do you confirm that your hosting address to indicate to neighbours/participants is the following:" + str(
                                 USER.s_home_location['street-address']) + ". Do you confirm? (y/n)")
                self.time_asked = datetime.now()
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos
                        USER.s_home_location['validated'] = True

                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            BOTSAY(USER, "I didn't recognize your address, can you retype it please?")
                            CLR_INBOX(USER)
                            self.time_asked = datetime.now()
                            STATE = 'wait for answer'
                            return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER, "Ok, got it, but this is too vague for a precise search. Can you retype your street address please?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER, "Thanks a lot, {}! ".format(USER.s_name or USER.s_name or ("Miss" if USER.gender == 'female' else "Mister")))
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait_for_answer_bis'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos
                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            results = corpus.process(msg.text)
                            infos.update(corp_get(results, 'boolean'))
                            infos.update(corp_get(results, 'tone'))
                            infos.update((corp_get(results, 'concern')))

                            if ('boolean' in infos and infos['boolean'] == False) or 'tone' in infos or 'concern' in infos:
                                BOTSAY(USER, "Ok, I guess you don't want to give you address! Let's continue the discussion anyway but just be aware that it's going to be more difficult to find something cool around you...")
                                CLR_INBOX(USER)
                                STATE = 'success'
                                return
                            else:
                                BOTSAY(USER, "I didn't recognize your address, can you retype it please?")
                                CLR_INBOX(USER)
                                self.time_asked = datetime.now()
                                STATE = 'wait_for_answer_bis'
                                return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER, "Ok, got it, but this is again too vague. Can you retype your street address?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER,
                                 "Thanks a lot, {}! From now, I will ask you questions related to what people like in your area. I will also suggest you activites I organize close to your home.".format(USER.s_name or USER.s_name or ("Miss" if USER.gender == 'female' else "Mister")))
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            USER.s_home_location['validated'] = True
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION ReAskLocation
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if 's_home_location' in USERDICT and 'confirmed' in USER.s_home_location and \
                        USER.s_home_location['confirmed'] is True:
            return 0.0
        if 's_home_location' in USERDICT and 'validated' in USER.s_home_location and \
                        USER.s_home_location['validated'] is True:
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        elif USER.last_channel_per_bot[BOT.name] in ["Telegram", "Facebook", "Line", "Viber"]:
            return 0.0
        else:
            return 0.4

    EXECUTE:

        START_STATE
            STATE = 'ask_confirmation'

        STATE_DEF 'ask_confirmation'
            BOTSAY(USER,
                         "I just wanna make sure I didn't miss-understood. Do you confirm your hosting address is the following?" + str(
                             USER.s_home_location['street-address']) + ". Do you confirm? (y/n)")
            STATE = 'wait_for_confirmation'
            self.time_asked = datetime.now()

        STATE_DEF 'wait_for_confirmation'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))

                if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                    BOTSAY(USER, "Cool")
                    CLR_INBOX(USER)
                    USER.s_home_location['confirmed'] = True
                    STATE = 'success'
                    return
                elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    BOTSAY(USER, "Ok! Give me your exact street address!")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait_for_confirmation' and self.get_state_calls_with_msg() >= 2:
                BOTSAY(USER,
                             "Do you confirm that your address is the following:" + str(
                                 USER.s_home_location['street-address']) + ". Do you confirm? (y/n)")
                self.time_asked = datetime.now()
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos
                        USER.s_home_location['confirmed'] = True

                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            BOTSAY(USER,
                                         "I didn't recognize your address, can you retype it please?")
                            CLR_INBOX(USER)
                            self.time_asked = datetime.now()
                            STATE = 'wait for answer'
                            return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER,
                                 "Ok, got it, but this is too vague for a precise search. Can you retype your street postal complete address please?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER, "Thanks a lot, {}! ".format(
                        USER.s_name or USER.s_name or (
                        "Miss" if USER.gender == 'female' else "Mister")))
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait_for_answer_bis'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        USER.s_home_location = infos
                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            results = corpus.process(msg.text)
                            infos.update(corp_get(results, 'boolean'))
                            infos.update(corp_get(results, 'tone'))
                            infos.update((corp_get(results, 'concern')))

                            if ('boolean' in infos and infos[
                                'boolean'] == False) or 'tone' in infos or 'concern' in infos:
                                BOTSAY(USER,
                                             "Ok, I guess you don't want to give you address! Let's continue the discussion anyway but just be aware that it's going to be more difficult to find something cool around you...")
                                CLR_INBOX(USER)
                                STATE = 'success'
                                return
                            else:
                                BOTSAY(USER,
                                             "I didn't recognize your address, can you retype it please?")
                                CLR_INBOX(USER)
                                self.time_asked = datetime.now()
                                STATE = 'wait_for_answer_bis'
                                return
                        USER.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    BOTSAY(USER,
                                 "Ok, got it, but this is again too vague. Can you retype your street address?")
                    CLR_INBOX(USER)
                    USER.general_location = reply
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.general_location))
                    self.time_asked = datetime.now()
                    USER.s_home_location = None
                    STATE = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    BOTSAY(USER,
                                 "Thanks a lot, {}! From now, I will ask you questions related to what people like in your area. I will also suggest you activites I organize close to your home.".format(
                                     USER.s_name or USER.s_name or (
                                     "Miss" if USER.gender == 'female' else "Mister")))
                    BOTSAY(USER, "Wayd developer: Data recorded:" + str(USER.s_home_location))
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            USER.s_home_location['confirmed'] = True
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION SendViral
    INPUT  user
        self.time_started = None

    USEFULNESS:
        if datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=0.1):
            return 0.0
        if INTER_CALLS == 0:
            # This interaction never ran before for this user
            return 0.05
        else:
            if TIME_SINCE_LAST_CALL > a_month:  # Every months. I don't want to spam too much my user
                return 0.05
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'wait'
            self.time_started = datetime.now()

        STATE_DEF 'wait'
            if (datetime.now() - self.time_started).total_seconds() > 4:  # Wait a bit after previous interaction before sending a lot of text
                STATE = 'say'

        STATE_DEF 'say'
            if USER.last_channel_per_bot[BOT.name] != "webchat":
                BOTSAY(USER, "I would highly appreciate if you recommend me to your friends. Why don't you share/transfer the next text message? So your friends can chat with me and maybe, you will meet them @ the activities I organize!!")
                if USER.last_channel_per_bot[BOT.name] == "Telegram":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!: https://t.me/JohnWaydBot ")
                elif USER.last_channel_per_bot[BOT.name] == "Line":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!: https://line.me/R/ti/p/TBD ")
                elif USER.last_channel_per_bot[BOT.name] == "Twilio":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!: here is her phone: +32460TBD")
                elif USER.last_channel_per_bot[BOT.name] == "Kik":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!: https://kik.me/John.Wayd")
                elif USER.last_channel_per_bot[BOT.name] == "Skype":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!: https://join.skype.com/bot/TBD")
                elif USER.last_channel_per_bot[BOT.name] == "Facebook":
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!:  http://m.me/JohnWaydBot")
                else:
                    BOTSAY(USER, "Hi my friend, I recommend you to chat with John Wayd! He is amazing!:  http://m.me/JohnWaydBot")
            else:
                BOTSAY(USER, "I would highly appreciate if you recommend me to your friends. Share the following link with all your friends (http://m.me/JohnWaydBot) and maybe, you will meet them @ the activities I organize!!")
            BOTSAY(USER, "One more thing... have a look at my last video on what I do: https://youtu.be/gdPsP3cdp0Y")
            STATE = 'success'

        STATE_DEF 'success'
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION DontDisturb
    """The goal here is to avoid spamming the user when he doesn't want to talk with us."""
    INPUT  user

    USEFULNESS:
        if 's_silent' not in USERDICT:
            return 0.0
        elif USER.s_silent is None or not USER.s_silent:
            return 0.0
        try:
            text = USER.s_silent.split("/")
            t1 = datetime.strptime(text[0],'%H:%M:%S')
            t2 = datetime.strptime(text[1],'%H:%M:%S')
            t3 = datetime.now()
            time1 = timedelta(hours=t1.hour, minutes=t1.minute)
            time2 = timedelta(hours=t2.hour, minutes=t2.minute)
            time3 = timedelta(hours=t3.hour, minutes=t3.minute)
            if time1 < time3 and time3 < time2:
                return 1.0
            return 0.0
        except:
            return 0.0

    EXECUTE:
        text = USER.s_silent.split("/")
        t1 = datetime.strptime(text[0], '%H:%M:%S')
        t2 = datetime.strptime(text[1], '%H:%M:%S')
        t3 = datetime.now()
        time1 = timedelta(hours=t1.hour, minutes=t1.minute)
        time2 = timedelta(hours=t2.hour, minutes=t2.minute)
        time3 = timedelta(hours=t3.hour, minutes=t3.minute)

        START_STATE
            STATE = 'silent'

        STATE_DEF 'silent'
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            elif time1 < time3 and time3 < time2:
                return
            else:
                STATE = 'success'
                return

        STATE_DEF 'success'
            LAUNCH_INTERACTION(Breath(BOT, USER))
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION Silent
    """The goal here is no avoid spamming the user when he doesn't want to talk with us.
    If the user wanna chat and is really reactive, then, a proactive discussion might be a good idea,
    if not, it might be good to talk only when necessary and avoid that the user feels spammed"""
    INPUT  user
        self.start = None

    USEFULNESS:

        if 's_time_of_last_message' not in USERDICT:
            return 0.0
        if USER.s_time_of_last_message is None or not USER.s_time_of_last_message:
            return 0.0
        delta = (datetime.now() - datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
        if delta > a_week:
            # The user is completely silent, don't disturb him except it necessary
            return 1.2
        elif delta > a_day*4:
            # The user is completely silent for 2 days, don't disturb him except it necessary
            return 0.9
        elif delta > a_day:
            # The user is completely silent for 1 days, don't disturb him except it necessary
            return 0.8
        elif delta > 60 * 60:
            # The user is completely silent for 1 hour, don't disturb him except it necessary
            return 0.7
        elif delta > 60 * 5:
            # The user is completely silent for 5 min, don't disturb him except it necessary
            return 0.45
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if INBOX[USER]:
                STATE = 'success'
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            elif (datetime.now() - self.start).total_seconds() < 60.0 * 60.0:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            RESETTING_INTERACTION
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------


INTERACTION Breath
    """ Just wait a bit and slow the discussion a bit to make it more natural when needed"""
    INPUT  user
        self.start = None

    USEFULNESS:
        if USER.last_message_sent_to_user is not None and USER.last_message_sent_to_user >= datetime.now() - timedelta(seconds=2):
            return 1.5
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if (datetime.now() - self.start).total_seconds() < 3:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION Breath2
    """ Just wait a bit and slow the discussion a bit to make it more natural when needed"""
    INPUT  user
        self.start = None

    USEFULNESS:
        if USER.last_message_sent_to_user is not None and USER.last_message_sent_to_user >= datetime.now() - timedelta(seconds=2):
            return 0.8
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if (datetime.now() - self.start).total_seconds() < 8:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskFriendContact
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=0.1):
            return 0.0
        if INTER_CALLS == 0:
            # This interaction never ran before for this user
            return 0.05
        else:
            if TIME_SINCE_LAST_CALL > a_day and datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=36):
                return 0.05
            else:
                return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "I would highly appreciate if you can send me the contact of a friend who might be interested to discuss with me. Please give me his/her mobile phone number (please use international format +xxxxx) or e-mail address and I'll contact him!")
            else:
                BOTSAY(USER, "I would highly appreciate if you can send me the contact of another friend who might be interested to discuss with me. Please give me his/her mobile phone number(please use international format +xxxxx) or e-mail address and I'll contact him!")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    reply = sa.get_info(msg.text, 'email')
                    if reply != {}:
                        infos.update({'email': reply})
                    reply = sa.get_info(msg.text, 'phone')
                    if reply != {}:
                        infos.update({'phone': reply})

                if 'email' in infos:
                    if SEARCH_CONTACT('Mail', infos['email']) is None:
                        text = "Hi, \n"
                        text += "I'm currently chatting via " + str(USER.last_channel_per_bot[BOT.name]) +" with your friend " + str(USER.s_name or "Mister X") + ".  \n"
                        if USER.gender == 'female':
                            text += "She"
                        else:
                            text += "He"
                        text += " probably did tell you about the Never Ending Run we organize. \n"
                        text += "\n"
                        text += "We will chat together and, one day, I might ask you : 'Are you up for a run in the next 45 min?' \n"
                        text += "A bunch of runners will pass by your place and pick you up for a run. \n"
                        text += "The group will go & pick up someone else in the area. \n"
                        text += "You can exit the group whenever you want. \n"
                        text += "This is the 'Never Ending Run'. \n"
                        text += "Be prepared to be part of a new world record. \n"
                        text += " \n"
                        text += "You can reach me on Facebook http://m.me/JohnWaydBot \n"
                        text += "but also on:   \n"
                        text += "Skype: https://join.skype.com/bot/d554b35f-7e92-4552-a3aa-9daef3f52b9f\n"
                        text += "Telegram: https://telegram.me/JohnWaydBot\n"
                        text += "Kik: https://kik.me/John.wayd\n"
                        text += "Line: https://line.me/R/ti/p/%40axq3438d\n"
                        text += "\n John  Wayd\n"
                        text +="https://youtu.be/OuaQrcMEM50\n"
                        text +="https://youtu.be/gdPsP3cdp0Y\n"
                        POSTMAIL(str(infos['email']), text)
                    else:
                        text = "Hi!\n" + str(USER.s_name or "Mister X")
                        text += " added you as a friend on the WAYD community.\n"
                        text += "I'll inform you when you might do an activity together.\n"
                        text += "\n John and Julia"
                        POSTMAIL(str(infos['email']), text)
                    BOTSAY(USER, "Thank you! I'll contact him and see if you can do an activity together!")
                    CLR_INBOX(USER)
                    STATE = 'success'

                if 'phone' in infos:
                    if SEARCH_CONTACT('Twilio', infos['phone']) is None:
                        if USER.last_channel_per_bot[BOT.name] == "Telegram":
                            text = "Hello! My name is John and " + str(USER.s_name if USER.s_name else "Mister X") + " told me you might be interested in running activities I organize. Check this out on http://t.me/JohnWaydBot   John"
                        else:
                            text = "Hello! My name is John and " + str(USER.s_name if USER.s_name else "Mister X") + " told me you might be interested in running activities I organize. Check this out on http://m.me/JohnWaydBot   John"

                        SENDSMS(str(infos['phone']), text)
                        BOTSAY(USER, "Thanks! I'll contact him and see if you can do an activity together!")
                    else:
                        BOTSAY(USER, "Thanks, I got it! Btw, your friend is already a WAYD user.")
                    CLR_INBOX(USER)
                    STATE = 'success'

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            LAUNCH_INTERACTION(Breath(BOT, USER))
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION TwilioLimit
    INPUT  user

    USEFULNESS:
        if USER.last_channel_per_bot[BOT.name] == 'Twilio' and USER.number_of_outgoing_messages and USER.s_number_of_incoming_messages and USER.number_of_outgoing_messages + USER.s_number_of_incoming_messages > 15.0:
            return 10.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'say'

        STATE_DEF 'say'
            if INBOX[USER] and USER.last_channel_per_bot[BOT.name] == "Twilio" and USER.s_number_of_incoming_messages and self.number_of_outgoing_messages and USER.number_of_outgoing_messages + USER.s_number_of_incoming_messages > 15.0:
                try:
                    BOTSAY(USER, "{}, let's discuss rather using facebook, skype, telegram or viber.".format(USER.s_name if USER.s_name else "Hey"))
                except:
                    BOTSAY(USER, "I suggest we discuss rather using http://m.me/20kmbrusselsBot")
                CLR_INBOX(USER)
                STATE = 'success'
            else:
                CLR_INBOX(USER)
                STATE = 'success'

        STATE_DEF 'success'
            # Do not remove the interaction
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------
