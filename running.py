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



# Master
from random import choice, randint, sample
from .greetings import ProcessSpontaneous
import itertools

from event import Event

# -----------------------------------------------------------------------------------------------------------------


INTERACTION AskAboutNER
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if 'like_NER' in USERDICT: #or USER.s_home_location is None:
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        try:
            return max(USER.demand_for_info['like_NER'] / n_hits, level_start_ask_about, CHANCE_THAT_USER_IS_INTERESTED_IN(USER, 'like_NER', 0.5)/100)
        except:
            return 0.05

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "Would you be interested to join a Never Ending Run? The idea is simple: One day, a bunch of runners might pass by your place and pick you up for a jogging. The group will then go & pick up someone else in the area. You can exit the group-run whenever you want. Aim is to beat the world record of the longest group-run ever. Interested? (y/n)")
            elif STATECALLS <= 2:
                BOTSAY(USER, "You haven't told me I think. Would you be up to participate to a Never Ending Run?")
            else:
                BOTSAY(USER, "Would you be up to participate to a Never Ending Run?")
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
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        USER.like_NER = 1.0
                        USER.currently_NER_available = 1.0
                        ADD_AGAIN_POSSIBLE(ProposeGroupNER(BOT, USER))
                    else:
                        USER.like_NER = -1.0
                    #BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_NER)))
                    CLR_INBOX(USER)

                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        USER.like_NER = 0.6
                    elif infos['sentiment'] == "unsure":
                        USER.like_NER = 0.2
                    else:
                        USER.like_NER = 0.0
                    #BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_NER)))
                    CLR_INBOX(USER)

                if USER.like_NER is not None and float(USER.like_NER) > 0.5:
                    BOTSAY(USER, lingua.ok() + " I'll see if a run is organized around your place and keep you posted!")
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif USER.like_NER is not None:
                    BOTSAY(USER, lingua.noprobs())
                    #BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_NER)))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION ProposeGroupNER
    INPUT  user
        self.num_min_people = 2.0

    USEFULNESS:
        if not USER.like_NER:
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0
        elif not INTER_CALLS or TIME_SINCE_LAST_CALL > a_week:
            # Suggest an activity (with user as a responsible user) every month. More is too much I think
            # 1. Find people nearby
            is_not_too_far = lambda u: DISTANCE(u, USER, "s_home_location") < 2000.0
            is_willing_to_do_NER = lambda u: u.like_NER and float(u.like_NER) > 0.8 and u.currently_NER_available > 0.9
            if COUNT_IF(lambda u: is_not_too_far(u) and is_willing_to_do_NER(u)) >= self.num_min_people:
                return level_start_suggest
            else:
                return 0.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            USER.currently_NER_available = 0
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "Would you be ready to leave your place in 5 min and go pick up someone else?")
            elif STATECALLS <= 2:
                BOTSAY(USER, "Ok to leave in 5 min?")
            else:
                BOTSAY(USER, "Ready to leave in 5 min?")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > 60 * 5:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        STATE = 'spread'
                    else:
                        STATE = 'success'
                    CLR_INBOX(USER)
                    BOTSAY(USER, lingua.ok())

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'spread'
            event = Event(str(randint(0, 1000000000)), 'NER')
            event.candidates = [] # the people who said yes for a run in the coming hour
            event.participants = [] # the current runners behind the flame
            event.planning = [] # (people, timing) in the planning
            event.s_location = USER.s_home_location # the currently location of the flame
            event.whosnext = 1000
            USER.currently_NER_available = 0
            event.responsible = USER # the currently holder of the flame
            USER.currently_NER_available = 0
            event.participants.append(USER)
            event.cummulatedrunners = [event.responsible]
            event.starttime = datetime.now()
            event.cummulateddistance = 0
            USER.NER_ready = datetime.now()
            USER.NER_asked = datetime.now()
            USER.NER_run = datetime.now()

            is_not_too_far = lambda u: DISTANCE(u, USER, "s_home_location") < 2000.0
            is_willing_to_do_NER = lambda u: u.like_NER and float(u.like_NER) > 0.8 and u.currently_NER_available > 0.9

            for candidate in SEARCH_IF(lambda u: is_not_too_far(u) and is_willing_to_do_NER(u)):
                if candidate is event.responsible:
                    candidate.NER_ready = datetime.now()
                    candidate.NER_asked = datetime.now()
                    candidate.NER_run = datetime.now()
                else:
                    LAUNCH_INTERACTION(ProposeRunNow(BOT, candidate, event))

            LAUNCH_INTERACTION(AnnounceNEREvent(BOT, event))
            STATE = 'success'

        STATE_DEF 'success'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION ProposeRunNow
    INPUT  user, event
        
        
        self.time_asked = None
        self.time_conf_asked = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask_for_confirmation'

        STATE_DEF 'ask_for_confirmation'

            if self.event.planning:
                timing = self.event.planning[-1][1] + DISTANCE(self.event.planning[-1][0], USER)/1000*60/8
            else:
                timing = DISTANCE(self.event.responsible, USER, topic='s_home_location')/1000*60/8

            for (j, (u, t)) in enumerate(self.event.planning):
                if j < len(self.event.planning) - 1 and DISTANCE(u, self.event.planning[j+1][0]) * 1.5 >= DISTANCE(u, USER) + DISTANCE(self.event.planning[j+1][0], USER):
                    timing = t + DISTANCE(u, USER)/1000*60/8
                    break

            BOTSAY(USER, "A Never Ending Run might pass by your place in the next {} (+-3) minutes. Are you up for a run?".format(int(timing)))
            USER.NER_asked = datetime.now()
            STATE = 'wait for confirmation'
            self.time_conf_asked = datetime.now()

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_conf_asked).total_seconds() > 3*60:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        STATE = 'success'
                        BOTSAY(USER, "Great!")
                        USER.NER_ready = datetime.now()
                        USER.currently_NER_available = 0
                        USER.NER_ready = datetime.now()
                        USER.NER_asked = datetime.now()
                        USER.NER_run = datetime.now()
                        self.event.candidates.append(USER)
                        BOTSAY(USER,"Ok, I'll check if the Never Ending Run can come to pick you up. I'll get back to you soon.")
                    else:
                        STATE = 'success'
                        BOTSAY(USER, "Ok! Maybe next time....")
                    CLR_INBOX(USER)
                    return
                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, that's not clear enough... Are you still interested?")
                        CLR_INBOX(USER)
                        return
                    elif infos['sentiment'] == "unsure":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still interested?")
                        CLR_INBOX(USER)
                        return
                    else:
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still interested....")
                        CLR_INBOX(USER)
                        return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return

            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask_for_confirmation'
                return

        STATE_DEF 'success'
            USER.NER_asked = datetime.now()
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            USER.NER_asked = datetime.now()
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION AnnounceNEREvent
    INPUT  event
        
        self.time_start = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'initial start'
            self.time_start = datetime.now()
            LAUNCH_INTERACTION(WhereToGoNext(BOT, self.event))

        STATE_DEF 'initial start'
            if (datetime.now() - self.time_start).total_seconds() > 15 * 60 or len(self.event.participants) + len(self.event.candidates) >= 2:
                STATE = 'event'

        STATE_DEF 'wait'
            if (datetime.now() - self.time_start).total_seconds() > 4 * 60:
                STATE = 'event'

        STATE_DEF 'event'
            if len(self.event.planning) == 0 and len(self.event.candidates) == 0:
                STATE = 'success'
                return

            saved_planning = self.event.planning.copy()
            saved_candidates = self.event.candidates.copy()

            # Insert candidates
            for (i, u) in enumerate(self.event.candidates):
                for (j, p) in enumerate(self.event.planning):
                    if j < len(self.event.planning)-1 and DISTANCE(self.event.planning[j][0], self.event.planning[j+1][0])*1.5 >= DISTANCE(self.event.planning[j][0], u)+DISTANCE(self.event.planning[j+1][0], u):
                        self.event.planning.insert(j+1, (u, None))
                        self.event.candidates.remove(u)

            ##############
            # Run here the sales men algo on remaining candidates
            ##############
            # Calculation of all lengths
            if self.event.candidates and len(self.event.candidates) > 1:
                data = []
                if self.event.planning:
                    data += self.event.planning[-1][0]
                data += self.event.candidates
                all_distances = [[DISTANCE(x, y) for y in data] for x in data]

                # initial value - just distance from 0 to every other point + keep the track of edges
                A = {(frozenset([0, idx + 1]), idx + 1): (dist, [0, idx + 1]) for idx, dist in enumerate(all_distances[0][1:])}
                cnt = len(all_distances)
                for m in range(2, cnt):
                    B = {}
                    for S in [frozenset(C) | {0} for C in itertools.combinations(range(1, cnt), m)]:
                        for j in S - {0}:
                            B[(S, j)] = min([(A[(S - {j}, k)][0] + all_distances[k][j], A[(S - {j}, k)][1] + [j]) for k in S if k != 0 and k != j])
                            # this will use 0th index of tuple for ordering, the same as if key=itemgetter(0) used
                    A = B
                res = min([(A[d][0] + all_distances[0][d[1]], A[d][1]) for d in iter(A)])
                # Append remaining candidates
                for i in res[1][1:]:
                    self.event.planning.append((self.event.candidates[i-1],None))
                    self.event.candidates.remove(self.event.candidates[i-1])
                self.event.candidates = []
            elif self.event.candidates and len(self.event.candidates) == 1:
                self.event.planning.append((self.event.candidates[0], None))
                self.event.candidates.remove(self.event.candidates[0])
                self.event.candidates = []

            # Recalculate timing of the planning
            for (i,(u, t)) in enumerate(self.event.planning):
                if i == 0:
                    if t is None:
                        self.event.planning[i] = (u, DISTANCE(u, self.event.responsible)/1000*60/8)
                else:
                    self.event.planning[i] = (u, self.event.planning[i-1][1]+DISTANCE(self.event.planning[i][0], self.event.planning[i-1][0])/1000*60/8)
            #print(self.event.planning)
            #print(self.event.candidates)
            for (i, (u, time)) in enumerate(self.event.planning):
                if u in saved_candidates:
                    # New in the planning
                    BOTSAY(u,"Congrats, You are in the planning of a Never Ending Run. The run will pass by your place in around {} minutes".format(int(time)))
                elif time < 25:
                    # Very close
                    BOTSAY(u, "The group is very close to your home now. The run will pass by your place in around {} minutes".format(int(time)))
                    LAUNCH_INTERACTION(AskConfirmation(BOT, USER, self.event))
                elif [abs(time-timing)/timing for (x, timing) in saved_planning if x is u][0] < 0.3:
                    pass
                else:
                    # Important change in the planning
                    BOTSAY(u, "The planning of the NeverEndingRun changed drastically. The run will pass by your place in around {} minutes".format(int(time)))
                    LAUNCH_INTERACTION(AskConfirmation(BOT, USER, self.event))
            toask = []
            for (i, (point, time)) in enumerate(self.event.planning):
                if len(self.event.planning) > 5:
                    is_not_too_far = lambda u: DISTANCE(u, point, "s_home_location") < 2000.0
                else:
                    is_not_too_far = lambda u: DISTANCE(u, point, "s_home_location") < 5000.0
                is_willing_to_do_NER = lambda u: u.like_NER and float(u.like_NER) > 0.8 and u.currently_NER_available > 0.9
                toask += SEARCH_IF(lambda u: is_not_too_far(u) and is_willing_to_do_NER(u) and u not in toask and u not in [x for (x, y) in self.event.planning])
            for u in toask:
                if (datetime.now() - u.NER_ready or datetime(2000,1,1)).total_seconds() < 60*60*4 and (datetime.now() - u.NER_asked or datetime(2000,1,1)).total_seconds() < 60*60 and  (datetime.now() - u.NER_run or datetime(2000,1,1)).total_seconds() < 60*60*24:
                    LAUNCH_INTERACTION(ProposeRunNow(BOT, u, self.event))

            if len(self.event.planning) <= 0 and len(self.event.candidates) == 0:
                STATE = 'success'
            else:
                STATE = 'wait'
                self.time_start = datetime.now()
        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(NERFinalResults(BOT, self.event))
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION AskConfirmation
    INPUT  user, event
        
        
        self.time_asked = None
        self.time_conf_asked = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask_for_confirmation'

        STATE_DEF 'ask_for_confirmation'
            BOTSAY(USER, "Do you confirm you will be ready in {} minutes? (without reply within 3 min, I consider it as a No)".format(int([t for i, (u, t) in enumerate(self.event.planning) if u is USER][0])))
            STATE = 'wait for confirmation'
            self.time_conf_asked = datetime.now()

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_conf_asked).total_seconds() > 3*60:
                BOTSAY(USER, "Without response from you, I put out of this Run. Sorry")
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1:
                    if infos['boolean'] == "true":
                        STATE = 'success'
                        BOTSAY(USER, "Great!")
                        USER.NER_ready = datetime.now()
                    else:
                        STATE = 'failure'
                        BOTSAY(USER, "Ok! Maybe next time....")
                    CLR_INBOX(USER)
                    return
                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, that's not clear enough... Are you ready?")
                        CLR_INBOX(USER)
                        return
                    elif infos['sentiment'] == "unsure":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still ready?")
                        CLR_INBOX(USER)
                        return
                    else:
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are ready....")
                        CLR_INBOX(USER)
                        return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return


        STATE_DEF 'success'
            USER.NER_ready = datetime.now()
            STATE = 'end'

        STATE_DEF 'failure'
            indexed = [i for i, (u, t) in enumerate(self.event.planning) if u is USER][0]
            self.event.planning.pop(indexed)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION WhereToGoNext
    INPUT  event
        
        self.time_start = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'initial start'
            self.time_start = datetime.now()

        STATE_DEF 'initial start'
            if (datetime.now() - self.time_start).total_seconds() > 15 * 60 or len(self.event.participants) + len(self.event.candidates) >= 2:
                STATE = 'wait'

        STATE_DEF 'wait'
            if self.event.whosnext > max(1.0, int(round(len(self.event.participants)/2))):
                STATE = 'event'

        STATE_DEF 'event'
            if len(self.event.planning) == 0 and len(self.event.candidates) == 0:
                STATE = 'success'
                return

            self.event.whosnext = 0
            fromperson = self.event.responsible
            nextperson = self.event.planning[0][0]
            ADD_AGAIN_POSSIBLE(ProcessSpontaneousForCurrentlyRunners(BOT, fromperson, self.event))
            self.event.responsible = nextperson
            self.event.cummulatedrunners.append(nextperson)
            self.event.cummulateddistance += DISTANCE(fromperson,self.event.responsible)
            BOTSAY(self.event.responsible, "The group is currently here: " + str(self.event.s_location) + " and running to your home to pick you up. Get ready!")
            self.event.s_location = nextperson.s_home_location

            for u in self.event.participants:
                BOTSAY(u, "Ok, now, run to the next person to pick up. " + ("His" if nextperson.gender is "male" else "Her") + " name is " + (nextperson.s_name or "King") +  " and is waiting for you here: " + str(self.event.s_location['street-address']) + " http://www.google.com/maps/place/" + str(self.event.s_location['lat']) + "," + str(self.event.s_location['lng']))
                BOTSAY(u, "When you get there, just send me a message 'Where to go next?' and I will tell you...")
            self.event.participants.append(nextperson)
            #self.event.planning[1][1] = DISTANCE(self.event.planning[1][0],self.event.responsible)/1000*60/8 + DISTANCE(fromperson,self.event.responsible)/1000*60/8/2
            self.event.planning.pop(0)
            STATE = "wait"

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION ProcessSpontaneousForCurrentlyRunners
    INPUT  user, event
        
        

    USEFULNESS:
        if INBOX[USER]:
            return 3.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'process'

        STATE_DEF 'process'
            if INBOX[USER] and USER.s_greeted_by_john is True:
                if INBOX[USER][-1].text == "poke":
                    pass
                else:
                    infos = {}
                    for msg in INBOX[USER]:
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'tone'))
                        infos.update(corp_get(results, 'ner'))

                    if 'ner' in infos:
                        if infos['ner'] == 'whosnext' and infos['ner_score'] > 0.5:  # 0. to too much,
                            self.event.whosnext += 1
                            BOTSAY(USER, "When enough runners ask me 'where to go next?', I'll inform you...")
                            STATE = 'success'
                            CLR_INBOX(USER)
                            return

                        if infos['ner'] == 'stoprunning' and infos['ner_score'] > 0.5:  # 0. to too much,
                            self.event.participants.remove(USER)
                            REMOVE_POSSIBLE(self)
                            BOTSAY(USER,  "Ok, understood. Have a safe run back home! See you later on a NeverEndingRun!")
                            USER.currently_NER_available = 1
                            STATE = 'success'
                            CLR_INBOX(USER)
                            return

                    answer = sa.is_general_question(INBOX[USER][-1].text)
                    if answer:
                        BOTSAY(USER, answer.replace("julia", "john").replace("Julia","John"))
                    else:
                        BOTSAY(USER, lingua.i_dont_understand_john())
            CLR_INBOX(USER)
            STATE = 'success'

        STATE_DEF 'success'
            STATE = 'end'
            RESETTING_INTERACTION

        STATE_DEF 'end'
            pass
# -------------------------------------------------------------------------------------------------------------------


INTERACTION NERFinalResults
    INPUT  event
        

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'say'

        STATE_DEF 'say'

            minutes = (datetime.now() - self.event.starttime).total_seconds()/60

            for u in self.event.cummulatedrunners:
                BOTSAY(u, "The NeverEndingRun where you participated in is now ended. You were " + str(len(self.event.cummulatedrunners))+ " participants.")
                BOTSAY(u, "With a run of " + str(int(self.event.cummulateddistance/1000)) + "meters done in " + str(int(minutes)) + " minutes,  the world record is not beated yet....Maybe next time...")
            STATE = "success"

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION AskAboutRunning
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if 'like_running' in USERDICT or USER.s_home_location is None:
            return 0.0
        if LAUNCHES and (TIME_SINCE_LAST_CALL < a_day or datetime.now() < datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        else:
            try:
                return max(USER.demand_for_info['like_running'] / n_hits, level_start_ask_about, CHANCE_THAT_USER_IS_INTERESTED_IN(USER, 'like_running', 0.5)/100)
            except:
                return 0.05

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "Do you like group running/jogging with neighbours? (y/n)")
            elif STATECALLS <= 2:
                BOTSAY(USER, "You haven't told me I think. Do you want to do group running/jogging?  (y/n)")
            else:
                BOTSAY(USER, "Do you like group jogging/running?  (y/n)")
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
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        USER.like_running = 1.0
                        # BOTSAY(USER,"My brother John Wayd will contact you if any group-run are organized in your area")
                        # BOTSAY(USER,"please poke other wayd bot:John")
                        ADD_AGAIN_POSSIBLE(ProposeGroupRunning(BOT, USER))
                    else:
                        USER.like_running = -1.0
                    BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_running)))
                    CLR_INBOX(USER)

                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        USER.like_running = 0.6
                    elif infos['sentiment'] == "unsure":
                        USER.like_running = 0.2
                    else:
                        USER.like_running = 0.0
                    BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_running)))
                    CLR_INBOX(USER)

                if USER.like_running is not None and float(USER.like_running) > 0.5:
                    if USER.max_dist is not None:
                        BOTSAY(USER, lingua.ok())
                        CLR_INBOX(USER)
                        STATE = 'success'
                        return
                    else:
                        BOTSAY(USER, "Ok, {}! And how far from your home (in km) should I search a group running event for you?".format(USER.s_name or ("Miss" if USER.gender == 'female' else "Mister")))
                        CLR_INBOX(USER)
                        STATE = 'wait for km'
                        return
                elif USER.like_running is not None:
                    BOTSAY(USER, lingua.noprobs())
                    BOTSAY(USER, "Wayd developer: Like Level recorded: {}".format(str(USER.like_running)))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait for km'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'success'
                return

            elif INBOX[USER]:
                for msg in INBOX[USER]:
                    reply = sa.get_info(msg.text, 'number')
                    if reply:
                        USER.max_dist_for_running = reply[0]
                if USER.max_dist_for_running is not None:
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(USER, "Wayd developer: Data recorded: {}km".format(str(USER.max_dist_for_running)))
                    CLR_INBOX(USER)
                    STATE = 'success'
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for km' and self.get_state_calls_with_msg() >= 2:
                BOTSAY(USER, "Any idea of the max km you are ready to do?")
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION ProposeGroupRunning
    INPUT  user
        self.num_min_people = 4.0

    USEFULNESS:
        if not USER.like_running:
            return 0.0
        elif not INTER_CALLS or TIME_SINCE_LAST_CALL > a_month:
            # Suggest an activity (with user as a responsible user) every month. More is too much I think
            # 1. Find people nearby
            defaultdistance = lambda u: min(float(u.max_dist)*1000, 20000.0) if u.max_dist else 2000.0
            distance = lambda u: min(float(u.max_dist_for_running)*1000, 200000.0) if u.max_dist_for_running else defaultdistance(u)
            is_not_too_far = lambda u: DISTANCE(u, USER, "s_home_location") < distance(u)
            is_willing_to_do_running = lambda u: u.like_running and float(u.like_running) > 0.8 and not u.running_proposal_ongoing
            if COUNT_IF(lambda u: is_not_too_far(u) and is_willing_to_do_running(u)) >= self.num_min_people:
                return level_start_suggest
            else:
                return 0.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'spread'

        STATE_DEF 'spread'
            event = Event(str(randint(0, 1000000000)), 'running')
            # We have to find a long term solution for this problem
            a = date.today()
            days = [a + timedelta(days=i) for i in range(1, 9)]
            event.possible_day = [str(x.strftime("%d/%m/%Y")) for x in days]
            event.votes = {key: [] for key in event.possible_day}
            event.candidates = []
            event.s_location = USER.s_home_location
            event.responsible = USER

            defaultdistance = lambda u: min(float(u.max_dist) * 1000, 20000.0) if u.max_dist else 2000.0
            distance = lambda u: min(float(u.max_dist_for_running) * 1000, 200000.0) if u.max_dist_for_running else defaultdistance(u)
            is_not_too_far = lambda u: DISTANCE(u, USER, "s_home_location") < distance(u)
            is_willing_to_do_running = lambda u: u.like_running and float(u.like_running) > 0.8 and not u.running_proposal_ongoing

            for candidate in SEARCH_IF(lambda u: is_not_too_far(u) and is_willing_to_do_running(u)):
                LAUNCH_INTERACTION(ChooseRunningDay(BOT, candidate, event))
                event.candidates.append(candidate)
                candidate.running_proposal_ongoing = 1.0

            LAUNCH_INTERACTION(AnnounceRunningEvent(BOT, event))
            STATE = 'success'

        STATE_DEF 'success'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION ChooseRunningDay
    INPUT  user, event
        
        
        self.time_asked = None
        self.time_conf_asked = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask_for_confirmation'

        STATE_DEF 'ask_for_confirmation'
            BOTSAY(USER, "I might be able to organize a group-run in your area with your neighbours this week. Are you still interested?")
            STATE = 'wait for confirmation'
            self.time_conf_asked = datetime.now()

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_conf_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                self.event.candidates.remove(USER)
                USER.running_proposal_ongoing = 0.0
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        STATE = 'ask'
                        BOTSAY(USER, "Great!")
                    else:
                        self.event.candidates.remove(USER)
                        STATE = 'success'
                        USER.running_proposal_ongoing = 0.0
                        BOTSAY(USER, "Ok! Maybe next time....")
                    BOTSAY(USER, "Wayd developer: Boolean recorded: {}".format(str(infos['boolean'])))
                    CLR_INBOX(USER)
                    return
                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, that's not clear enough... Are you still interested?")
                        CLR_INBOX(USER)
                        return
                    elif infos['sentiment'] == "unsure":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still interested?")
                        CLR_INBOX(USER)
                        return
                    else:
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still interested....")
                        CLR_INBOX(USER)
                        return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask_for_confirmation'
                return

        STATE_DEF 'ask'
            BOTSAY(USER, "Ok then... Tell me the days when you are available for a group-run (it will be in the evening...) " + "(Friday? Saturday and sunday? Next monday and friday? The 01/06?)")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                self.event.candidates.remove(USER)
                USER.running_proposal_ongoing = 0.0
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    reply = sa.get_info(msg.text, 'date')
                    if reply != {}:
                        infos.update({'date': reply})

                if 'date' in infos:
                    answer = [str(datetime.strptime(x, '%Y-%m-%d').date().strftime("%d/%m/%Y")) for x in infos['date']]
                    answer = list(set(answer))
                    for i in answer:
                        if i in self.event.possible_day:
                            self.event.votes[i].append(USER)
                    try:
                        self.event.candidates.remove(USER)
                    except:
                        pass
                    BOTSAY(USER, lingua.ok())

                else:
                    try:
                        self.event.candidates.remove(USER)
                    except:
                        pass
                    USER.running_proposal_ongoing = 0.0
                CLR_INBOX(USER)
                STATE = 'success'
                return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION AnnounceRunningEvent
    INPUT  event
        

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'event'

        STATE_DEF 'event'
            if len(self.event.candidates) > 0:
                return

            self.event.s_day = max(self.event.votes, key=lambda x: len(set(self.event.votes[x])))
            self.event.participants.extend(self.event.votes[self.event.s_day])

            if len(self.event.candidates) == 0 and len(self.event.participants) < 2:  # The value here is super important!!!
                for u in self.event.participants:
                    u.running_proposal_ongoing = 0.0
                STATE = 'end'
            else:
                if self.event.responsible not in self.event.participants:
                    self.event.responsible = self.event.participants[0]
                    self.event.s_location = self.event.participants[0].s_home_location
                ndays = int((datetime.strptime(self.event.s_day, '%d/%m/%Y') - datetime.today()).days + 1)
                self.event.forecast = sa.get_weather_forecast(self.event.s_location['lat'], self.event.s_location['lng'], ndays)
                for u in self.event.participants:
                    BOTSAY(u, "You will be running with " + str(len(self.event.participants)-1) + " other people on the " + str(self.event.s_day) +" at " +  str(self.event.s_hour))
                    BOTSAY(u, "I will send you a reminder 1h before. Forecast expect to have a weather " + self.event.forecast['weather'].lower())
                    BOTSAY(u, "The running event will start here: " + str(self.event.s_location['street-address']) + " http://www.google.com/maps/place/" + str(self.event.s_location['lat']) + "," + str(self.event.s_location['lng']))
                    a = str(self.event.s_day).split("/")
                    b = str(self.event.s_hour).split(("."))
                    googlestring = a[2]+a[1]+a[0]+'T'+b[0]+b[1]+'00Z/'+ a[2]+a[1]+a[0]+'T'+str(min(int(b[0])+self.event.duration,23)).replace(".", "")+b[1]+'00Z'
                    # googlestring should look like this: "20170127T224000Z/20170320T221500Z"
                    BOTSAY(u, "Link to add to your calendar: https://calendar.google.com/calendar/render?action=TEMPLATE&text=bbq+WAYD&dates="+googlestring)
                STATE = 'success'
        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            ADD_POSSIBLE(RunningEventReminder(BOT, self.event))
            ADD_POSSIBLE(LastMinuteConfirmationRunningEvent(BOT, self.event))
            ADD_POSSIBLE(LastMinuteCancelRunningEvent(BOT, self.event))
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION LastMinuteConfirmationRunningEvent
    INPUT  event
        

    USEFULNESS:
        t = datetime.strptime(self.event.s_hour, '%H.%M')
        d = datetime.strptime(self.event.s_day, "%d/%m/%Y")
        if datetime.now() >= d + timedelta(hours=t.hour - 4.0, minutes=t.minute):
            return 1.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask-confirm'

        STATE_DEF 'ask-confirm'
            self.event.forecast = sa.get_weather_forecast(int(self.event.s_location.lat), int(self.event.s_location.lng), 0)
            for u in self.event.participants:
                QUERE_INTERACTION(LastMinuteConfirmationRunningEvent2(BOT, u, self.event))
            STATE = 'success'
        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass

# -----------------------------------------------------------------------------------------------------------------------


INTERACTION LastMinuteConfirmationRunningEvent2
    INPUT  user, event
        
        
        self.time_asked = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask_for_confirmation'

        STATE_DEF 'ask_for_confirmation'
            BOTSAY(USER, "You will have a running event with " + str(len(self.event.participants) - 1) + " other people later today at " + str(self.event.s_hour))
            BOTSAY(USER, "Do you confirm you will come?")
            self.time_asked = datetime.now()
            STATE = 'wait for confirmation'

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                self.event.participants.remove(USER)
                USER.running_proposal_ongoing = 0.0
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'sentiment'))
                    infos.update(corp_get(results, 'activity'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1 and 'activity' not in infos:
                    if infos['boolean'] == "true":
                        BOTSAY(USER, "Great!")
                    else:
                        self.event.candidates.remove(USER)
                        USER.running_proposal_ongoing = 0.0
                        BOTSAY(USER, "Ok! Understood. Enjoy the evening!")
                    BOTSAY(USER, "Wayd developer: Boolean recorded: {}".format(str(infos['boolean'])))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif 'sentiment' in infos and infos['sentiment_score'] > 0.1:
                    if infos['sentiment'] == "maybe":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, that's not clear enough... Are you still in for tonight?")
                        CLR_INBOX(USER)
                        return
                    elif infos['sentiment'] == "unsure":
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still in for tonight?")
                        CLR_INBOX(USER)
                        return
                    else:
                        STATE = 'wait for confirmation'
                        BOTSAY(USER, "Well, I need to know if you are still in for tonight....")
                        CLR_INBOX(USER)
                        return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask_for_confirmation'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass

# -----------------------------------------------------------------------------------------------------------------------


INTERACTION LastMinuteCancelRunningEvent
    INPUT  event
        

    USEFULNESS:
        t = datetime.strptime(self.event.s_hour, '%H.%M')
        d = datetime.strptime(self.event.s_day, "%d/%m/%Y")
        if len(self.event.participants) < 2:
            return 1.0
        elif datetime.now() >= d + timedelta(hours=t.hour + 4.0, minutes=t.minute):
            return 1.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'cancel'

        STATE_DEF 'cancel'
            t = datetime.strptime(self.event.s_hour, '%H.%M')
            d = datetime.strptime(self.event.s_day, "%d/%m/%Y")
            if len(self.event.participants) < 2:
                for u in self.event.participants:
                    self.event.participants.remove(u)
                    u.running_proposal_ongoing = 0.0
                    BOTSAY(u, "The event tonight is cancelled. Sorry for that. Too many people declined.")
                STATE = 'success'
            elif datetime.now() >= d + timedelta(hours=t.hour + 4.0, minutes=t.minute):
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass

# -----------------------------------------------------------------------------------------------------------------------


INTERACTION RunningEventReminder
    INPUT  event
        

    USEFULNESS:
        t = datetime.strptime(self.event.s_hour, '%H.%M')
        d = datetime.strptime(self.event.s_day, "%d/%m/%Y")
        if datetime.now() >= d + timedelta(hours=t.hour-1.0, minutes=t.minute):
            return 1.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'remind'

        STATE_DEF 'remind'

            if self.event.responsible not in self.event.participants:
                self.event.responsible = self.event.participants[0]
                self.event.s_location = self.event.participants[0].s_home_location
                for u in self.event.participants:
                    BOTSAY(u, "I remind you that you will be running with other people in an hour. You can already prepare your shoes!")
                    BOTSAY(u, "The running event is with " + str(len(self.event.participants)) + " participants including you and will start in a NEW PLACE: " + str(self.event.s_location['street-address']) + " http://www.google.com/maps/place/" + str(self.event.s_location['lat']) + "," + str(self.event.s_location['lng']))

            else:
                for u in self.event.participants:
                    BOTSAY(u, "I remind you that you will be running with other people in an hour. You can already prepare your shoes!")
                    BOTSAY(u, "The running event is with " + str(len(self.event.participants)) + " participants including you and will start here: http://www.google.com/maps/place/" + str(self.event.s_location['lat']) + "," + str(self.event.s_location['lng']))

            STATE = 'success'
        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'
        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass

# -----------------------------------------------------------------------------------------------------------------------


INTERACTION RunningEventEnd
    INPUT  event
        

    USEFULNESS:
        t = datetime.strptime(self.event.s_hour, '%H.%M')
        d = datetime.strptime(self.event.s_day, "%d/%m/%Y")
        if datetime.now() >= d + timedelta(hours=t.hour + 5.0, minutes=t.minute):
            return 1.0
        else:
            return 0.0

    EXECUTE:

        START_STATE
            STATE = 'stretch'

        STATE_DEF 'stretch'

            for u in self.event.participants:
                BOTSAY(u, "I hope the event went well! I advice you to stretch a bit")
                u.running_proposal_ongoing = 0.0
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

