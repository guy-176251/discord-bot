import pickle
import discord
from discord.ext.commands import Context

WIN = 'win'
LOSE = 'lose'

class ScoreKeeper:
    '''
    scoreboard = {
        user: {user1: int, }
    }
    '''

    __file_name = 'scoreboard'

    try:
        with open(__file_name, 'rb') as f:
            __board = pickle.load(f)
    except:
        print('scoreboard not loaded')
        __board = {}

    def __getitem__(self, user_id: int) -> dict:
        '''Returns dict of all the players the user_id scored on.

        { user_id (int): { win: score_number (int), lose: score_number (int) } }
        '''

        self.__board.setdefault(user_id, {})
        return self.__board[user_id]

    def clear(self, scorer: int, scoree: int):
        try:
            self.__board[scorer].pop(scoree)
        except: pass

    def score(self, scorer: int, scoree: int, if_win: bool):

        if if_win:
            mode = WIN
        else:
            mode = LOSE

        self.__board.setdefault(scorer, {})
        self.__board[scorer].setdefault(scoree, {WIN: 0, LOSE: 0})

        self.__board[scorer][scoree][mode] += 1

        with open(self.__file_name, 'wb') as f:
            pickle.dump(self.__board, f)

scorekeeper = ScoreKeeper()

def embed_maker(ctx: Context):
    member_ids = [member.id for member in ctx.guild.members]
    record     = scorekeeper[ctx.message.author.id]

    if not record or not any(user_id in member_ids for user_id in record):
        return None

    title  = f'__Record for {ctx.message.author.nick or ctx.message.author.name}__'
    embeds = [discord.Embed(title = title)]

    for user_id in record:
        if len(embeds[-1].fields) == 25:
            embeds.append(discord.Embed(title = title))

        member = ctx.guild.get_member(user_id)

        embeds[-1].add_field(name = member.nick or member.name,
                             value = f'{record[user_id][WIN]} - {record[user_id][LOSE]}')

    return embeds
