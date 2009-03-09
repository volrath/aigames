class StateMachine(object):
    """
    Singleton class (?)
    """

    @classmethod
    def fuzzy_life(cls, character, game):
        """
        Given a character and the game, it calculates the sight of
        pursuing or evading that the character has to have depending on
        his current energy. The more alive he is, the more he will pursue.
        """
        try:
            pursue_evade = character.behaviors['pursue_evade']
        except KeyError:
            return
        pursue = pursue_evade.behavior_set['Pursue']
        evade  = pursue_evade.behavior_set['Evade']
        if not hasattr(pursue, 'args'):
            setattr(pursue, 'args', {})
        if not hasattr(evade, 'args'):
            setattr(evade, 'args', {})
        pursue.args['characters_sight'] = 40. * (character.energy / 100.)
        evade.args['characters_sight']  = 40. - pursue.args['characters_sight']
