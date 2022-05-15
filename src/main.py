import json
import re

from pyrogram import Client, Filters
from pyrogram import (InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      CallbackQuery)

import functions as func
import raid_dynamax as raid

from Config import Config

app = Client(
    api_id=Config.aid,
    api_hash=Config.ahash,
    bot_token=Config.bot_token,
    session_name='inhunmanDexBot'
)

texts = json.load(open('src/texts.json', 'r'))
data = json.load(open('src/pokedex.json', 'r'))
stats = json.load(open('src/stats.json', 'r'))
jtype = json.load(open('src/type.json', 'r'))

usage_dict = {'vgc': None}
raid_dict = {}


# ===== Stats =====
@app.on_message(Filters.private & Filters.create(lambda _, message: str(message.chat.id) not in stats['users']))
@app.on_message(Filters.group & Filters.create(lambda _, message: str(message.chat.id) not in stats['groups']))
def get_bot_data(app, message):
    cid = str(message.chat.id)
    if message.chat.type == 'private':
        stats['users'][cid] = {}
        name = message.chat.first_name
        try:
            name = message.chat.first_name + ' ' + message.chat.last_name
        except TypeError:
            name = message.chat.first_name
        stats['users'][cid]['name'] = name
        try:
            stats['users'][cid]['username'] = message.chat.username
        except AttributeError:
            pass

    elif message.chat.type in ['group', 'supergroup']:
        stats['groups'][cid] = {}
        stats['groups'][cid]['title'] = message.chat.title
        try:
            stats['groups'][cid]['username'] = message.chat.username
        except AttributeError:
            pass
        stats['groups'][cid]['members'] = app.get_chat(cid).members_count

    json.dump(stats, open('src/stats.json', 'w'), indent=4)
    print(stats)
    print('\n\n')
    message.continue_propagation()


@app.on_message(Filters.command(['stats', 'stats@pokedexkingbot']))
def get_stats(app, message):
    if message.from_user.id in Config.sudo:
        members = 0
        for group in stats['groups']:
            members += stats['groups'][group]['members']
        text = texts['stats'].format(
            len(stats['users']),
            len(stats['groups']),
            members
        )
        app.send_message(
            chat_id=message.chat.id,
            text=text
        )


# ===== Home =====
@app.on_message(Filters.command(['start', 'start@pokeDexkingBot']))
def start(app, message):
    app.send_message(
        chat_id=message.chat.id,
        text=texts['start_message'],
        parse_mode='HTML'
    )

# ==== Type Pokemon =====
@app.on_message(Filters.command(['type', 'type@pokedexkingBot']))
def ptype(app, message):
    try:
        gtype = message.text.split(' ')[1]
    except IndexError as s:
        app.send_message(
            chat_id=message.chat.id,
            text="`Syntex error: use eg '/type poison'`"
        )
        return
    try:
        data = jtype[gtype.lower()]
    except KeyError as s:
        app.send_message(
            chat_id=message.chat.id,
            text=("`This type doesn't exist good sir :/ `\n"
                  "`Do  /types  to check for the existing types.`")
        )
        return
    strong_against = ", ".join(data['strong_against'])
    weak_against = ", ".join(data['weak_against'])
    resistant_to = ", ".join(data['resistant_to'])
    vulnerable_to = ", ".join(data['vulnerable_to'])
    keyboard = ([[
        InlineKeyboardButton('All Types',callback_data=f"hexa_back_{message.from_user.id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Type  :  `{gtype.lower()}`\n\n"
              f"Strong Against:\n`{strong_against}`\n\n"
              f"Weak Against:\n`{weak_against}`\n\n"
              f"Resistant To:\n`{resistant_to}`\n\n"
              f"Vulnerable To:\n`{vulnerable_to}`"),
        reply_markup=InlineKeyboardMarkup(keyboard)
           
    )

# ==== Typew List =====
def ptype_buttons(user_id):
    keyboard = ([[
        InlineKeyboardButton('Normal',callback_data=f"type_normal_{user_id}"),
        InlineKeyboardButton('Fighting',callback_data=f"type_fighting_{user_id}"),
        InlineKeyboardButton('Flying',callback_data=f"type_flying_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Poison',callback_data=f"type_poison_{user_id}"),
        InlineKeyboardButton('Ground',callback_data=f"type_ground_{user_id}"),
        InlineKeyboardButton('Rock',callback_data=f"type_rock_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Bug',callback_data=f"type_bug_{user_id}"),
        InlineKeyboardButton('Ghost',callback_data=f"type_ghost_{user_id}"),
        InlineKeyboardButton('Steel',callback_data=f"type_steel_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Fire',callback_data=f"type_fire_{user_id}"),
        InlineKeyboardButton('Water',callback_data=f"type_water_{user_id}"),
        InlineKeyboardButton('Grass',callback_data=f"type_grass_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Electric',callback_data=f"type_electric_{user_id}"),
        InlineKeyboardButton('Psychic',callback_data=f"type_psychic_{user_id}"),
        InlineKeyboardButton('Ice',callback_data=f"type_ice_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Dragon',callback_data=f"type_dragon_{user_id}"),
        InlineKeyboardButton('Fairy',callback_data=f"type_fairy_{user_id}"),
        InlineKeyboardButton('Dark',callback_data=f"type_dark_{user_id}")]])
    keyboard += ([[
        InlineKeyboardButton('Delete',callback_data=f"hexa_delete_{user_id}")]])
    return keyboard
    
@app.on_message(Filters.command(['types', 'types@pokedexkingBot']))
def types(app, message): 
    user_id = message.from_user.id
    app.send_message(
        chat_id=message.chat.id,
        text="List of types of Pokemons:",
        reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
    )

# ===== Types Callback ====
@app.on_callback_query(Filters.create(lambda _, query: 'type_' in query.data))
def button(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[0]
    type_n = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if cuser_id == user_id:
        if query_data == "type":
            data = jtype[type_n]
            strong_against = ", ".join(data['strong_against'])
            weak_against = ", ".join(data['weak_against'])
            resistant_to = ", ".join(data['resistant_to'])
            vulnerable_to = ", ".join(data['vulnerable_to'])
            keyboard = ([[
            InlineKeyboardButton('Back',callback_data=f"hexa_back_{user_id}")]])
            callback_query.message.edit_text(
                text=(f"Type  :  `{type_n}`\n\n"
                f"Strong Against:\n`{strong_against}`\n\n"
                f"Weak Against:\n`{weak_against}`\n\n"
                f"Resistant To:\n`{resistant_to}`\n\n"
                f"Vulnerable To:\n`{vulnerable_to}`"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
    

@app.on_callback_query(Filters.create(lambda _, query: 'hexa_' in query.data))
def button2(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1]
    user_id = int(q_data.split('_')[2])
    cuser_id = callback_query.from_user.id
    if user_id == cuser_id:
        if query_data == "back":
            callback_query.message.edit_text(
                "List of types of Pokemons:",
                reply_markup=InlineKeyboardMarkup(ptype_buttons(user_id))
            )
        elif query_data == "delete":
            callback_query.message.delete()
        else:
            return
    else:
        callback_query.answer(
            text="You can't use this button!",
            show_alert=True
        )
  
# ===== Pokemon Type Command ======
@app.on_message(Filters.command(['ptype', 'ptype@pokedexkingBot']))
def poketypes(app, message): 
    user_id = message.from_user.id
    try:
        arg = message.text.split(' ')[1].lower()
    except IndexError:
        app.send_message(
            chat_id=message.chat.id,
            text=("`Syntex error: use eg '/ptype pokemon_name'`\n"
                  "`eg /ptype Pikachu`")
        )
        return  
    try:
        p_type = data[arg][arg]['type']
    except KeyError:
        app.send_message(
            chat_id=message.chat.id,
            text="`This pokemon doesn't exist good sir :/`"
        )
        return
    
    try:
        get_pt = f"{p_type['type1']}, {p_type['type2']:}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}"),
        InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{arg}_{user_id}")]])
    except KeyError:
        get_pt = f"{p_type['type1']}"
        keyboard = ([[
        InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{arg}_{user_id}")]])
    app.send_message(
        chat_id=message.chat.id,
        text=(f"Pokemon: `{arg}`\n\n"
              f"Types: `{get_pt}`\n\n"
              "__Click the button below to get the attact type effectiveness!__"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
@app.on_callback_query(Filters.create(lambda _, query: 'poket_' in query.data))
def poketypes_callback(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    pt_name = q_data.split('_')[2]
    user_id = int(q_data.split('_')[3])  
    if callback_query.from_user.id == user_id:  
        data = jtype[query_data]
        strong_against = ", ".join(data['strong_against'])
        weak_against = ", ".join(data['weak_against'])
        resistant_to = ", ".join(data['resistant_to'])
        vulnerable_to = ", ".join(data['vulnerable_to'])
        keyboard = ([[
        InlineKeyboardButton('Back',callback_data=f"pback_{pt_name}_{user_id}")]])
        callback_query.message.edit_text(
            text=(f"Type  :  `{query_data}`\n\n"
            f"Strong Against:\n`{strong_against}`\n\n"
            f"Weak Against:\n`{weak_against}`\n\n"
            f"Resistant To:\n`{resistant_to}`\n\n"
            f"Vulnerable To:\n`{vulnerable_to}`"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allow to use this!",
            show_alert=True
        )
    
@app.on_callback_query(Filters.create(lambda _, query: 'pback_' in query.data))
def poketypes_back(client: app, callback_query: CallbackQuery):
    q_data = callback_query.data
    query_data = q_data.split('_')[1].lower()
    user_id = int(q_data.split('_')[2]) 
    if callback_query.from_user.id == user_id:
        p_type = data[query_data][query_data]['type']
        try:
            get_pt = f"{p_type['type1']}, {p_type['type2']:}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}"),
            InlineKeyboardButton(p_type['type2'],callback_data=f"poket_{p_type['type2']}_{query_data}_{user_id}")]])
        except KeyError:
            get_pt = f"{p_type['type1']}"
            keyboard = ([[
            InlineKeyboardButton(p_type['type1'],callback_data=f"poket_{p_type['type1']}_{query_data}_{user_id}")]])
        callback_query.message.edit_text(
            (f"Pokemon: `{query_data}`\n\n"
             f"Types: `{get_pt}`\n\n"
             "__Click the button below to get the attact type effectiveness!__"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        callback_query.answer(
            text="You're not allow to use this!",
            show_alert=True
        )
    
        
# ===== Data command =====
@app.on_callback_query(Filters.create(lambda _, query: 'basic_infos' in query.data))
@app.on_message(Filters.command(['data', 'data@pokedexkingbot']))
def pkmn_search(app, message):
    try:
        if message.text == '/data' or message.text == '/data@pokedexkingBot':
            app.send_message(message.chat.id, texts['error1'], parse_mode='HTML')
            return None
        pkmn = func.find_name(message.text)
        result = func.check_name(pkmn, data)

        if type(result) == str:
            app.send_message(message.chat.id, result)
            return None
        elif type(result) == list:
            best_matches(app, message, result)
            return None
        else:
            pkmn = result['pkmn']
            form = result['form']
    except AttributeError:
        pkmn = re.split('/', message.data)[1]
        form = re.split('/', message.data)[2]


    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=True)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=True)

    markup_list = [[
        InlineKeyboardButton(
            text='➕ Expand',
            callback_data='all_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️👊 Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🌲🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, message, text, markup)


def best_matches(app, message, result):
    text = texts['results']
    emoji_list = ['1️⃣', '2️⃣', '3️⃣']
    index = 0
    for dictt in result:
        pkmn = dictt['pkmn']
        form = dictt['form']
        percentage = dictt['percentage']
        form_name = data[pkmn][form]['name']
        name = func.form_name(pkmn.title(), form_name)
        text += '\n{} <b>{}</b> (<i>{}</i>)'.format(
            emoji_list[index],
            name,
            percentage
        )
        if index == 0:
            text += ' [<b>⭐️ Top result</b>]'
        index += 1
    app.send_message(message.chat.id, text, parse_mode='HTML')


@app.on_callback_query(Filters.create(lambda _, query: 'all_infos' in query.data))
def all_infos(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    
    if pkmn in form:
        text = func.set_message(data[pkmn][form], reduced=False)
    else:
        base_form = re.sub('_', ' ', pkmn.title())
        name = base_form + ' (' + data[pkmn][form]['name'] + ')'
        text = func.set_message(data[pkmn][form], name, reduced=False)

    markup_list = [[
        InlineKeyboardButton(
            text='➖ Reduce',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='⚔️👊 Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        ),
        InlineKeyboardButton(
            text='🌲🏠 Locations',
            callback_data='locations/'+pkmn+'/'+form
        )
    ]]
    for alt_form in data[pkmn]:
        if alt_form != form:
            markup_list.append([
                InlineKeyboardButton(
                    text=data[pkmn][alt_form]['name'],
                    callback_data='basic_infos/'+pkmn+'/'+alt_form
                )
            ])
    markup = InlineKeyboardMarkup(markup_list)

    func.bot_action(app, call, text, markup)


@app.on_callback_query(Filters.create(lambda _, query: 'moveset' in query.data))
def moveset(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]
    if len(re.split('/', call.data)) == 4:
        page = int(re.split('/', call.data)[3])
    else:
        page = 1
    dictt = func.set_moveset(pkmn, form, page)

    func.bot_action(app, call, dictt['text'], dictt['markup'])


@app.on_callback_query(Filters.create(lambda _, query: 'locations' in query.data))
def locations(app, call):
    pkmn = re.split('/', call.data)[1]
    form = re.split('/', call.data)[2]

    text = func.get_locations(data, pkmn)

    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='⚔️ Moveset',
            callback_data='moveset/'+pkmn+'/'+form
        )
    ],
    [
        InlineKeyboardButton(
            text='🔙 Back to basic infos',
            callback_data='basic_infos/'+pkmn+'/'+form
        )
    ]])

    func.bot_action(app, call, text, markup)


# ===== Usage command =====
@app.on_callback_query(Filters.create(lambda _, query: 'usage' in query.data))
@app.on_message(Filters.command(['usage', 'usage@pokedexkingBot']))
def usage(app, message):
    try:
        page = int(re.split('/', message.data)[1])
        dictt = func.get_usage_vgc(int(page), usage_dict['vgc'])
    except AttributeError:
        page = 1
        text = '<i>Connecting to Pokémon Showdown database...</i>'
        message = app.send_message(message.chat.id, text, parse_mode='HTML')
        dictt = func.get_usage_vgc(int(page))
        usage_dict['vgc'] = dictt['vgc_usage']

    leaderboard = dictt['leaderboard']
    base_text = texts['usage']
    text = ''
    for i in range(15):
        pkmn = leaderboard[i]
        text += base_text.format(
            pkmn['rank'],
            pkmn['pokemon'],
            pkmn['usage'],
        )
    markup = dictt['markup']

    func.bot_action(app, message, text, markup)


# ===== FAQ command =====
@app.on_message(Filters.command(['faq', 'faq@poledexkingBot']))
def faq(app, message):
    text = texts['faq']
    app.send_message(
        chat_id=message.chat.id,
        text=text, 
        parse_mode='HTML',
        disable_web_page_preview=True
    )



# ===== About command =====
@app.on_message(Filters.command(['about', 'about@pokedexkingBot']))
def about(app, message):
    text = texts['about']
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text='Github',
            url='https://github.com/amritraj2008'
        )
    ]])

    app.send_message(
        chat_id=message.chat.id,
        text=text, 
        reply_markup=markup,
        disable_web_page_preview=True
    )

# ======= common commands ========




url_nature = 'https://img.rankedboost.com/wp-content/uploads/2016/08/pokemon-go-natures.jpg'
f = open('out.jpg','wb')
f.write(urllib.request.urlopen(url_nature).read())
f.close()


@app.on_message(Filters.command(['nature', 'nature@pokedexkingBot']))

def send_photo(message):
    tb.send_chat_action(message.chat.id, 'upload_photo')
    img = open('out.jpg', 'rb')
    @app.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
    img.close()

@app.on_message(Filters.command=['start', 'start@pokedexkingbot'])
def start(message):
    app.reply_to(message,f'✨ Hello @{message.from_user.username} ✨\n\n✨ I am PokeDex Bot ✨\n\n✨ My Master Is @amritraj20_08 ✨\n\n✨Add Me To Group And I will help you by providing informaton about pokemon Related Facts✨')

@app.on_message(Filters.command=['hardy','docile','serious','bashful','quirky','Hardy','Docile','Serious','Bashful','Quirky','hardy@pokedexkingbot','docile@pokedexkingbot','serious@pokedexkingbot','bashful@pokedexkingbot','Quirky@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - None\n➖ Stats Decrease - None')

@app.on_message(Filters.command=['guide','guide@pokedexkingbot'])
def guide(message):
    app.reply_to(message,'https://telegra.ph/A-Beginners-Guide-to-HeXa-02-06')

@app.on_message(Filters.command=['timid','timid@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Speed\n➖ Stats Decrease - Attack')

@app.on_message(command=['jolly','Jolly@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Speed\n➖ Stats Decrease - Sp.Attack')

@app.on_message(command=['hasty','hasty@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Speed\n➖ Stats Decrease - Defence')

@app.on_message(command=['naive','naive@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Speed\n➖ Stats Decrease - Sp.Defence')

@app.on_message(command=['lonely','lonely@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Attack\n➖ Stats Decrease - Defence')

@app.on_message(command=['brave','brave@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Attack\n➖ Stats Decrease - Speed')

@app.on_message(command=['adamant','adamant@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Attack\n➖ Stats Decrease - Sp.Attack')

@app.on_message(command=['naughty','naughty@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Attack\n➖ Stats Decrease - Sp.Defence')

@app.on_message(command=['modest','modest@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Attack\n➖ Stats Decrease - Attack')

@app.on_message(command=['rash','rash@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Attack\n➖ Stats Decrease - Sp.Defence')

@app.on_message(command=['mild','mild@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Attack\n➖ Stats Decrease - Defence')

@app.on_message(command=['quite','quite@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Attack\n➖ Stats Decrease - Speed')

@app.on_message(command=['calm','calm@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Defence\n➖ Stats Decrease - Attack')

@app.on_message(command=['careful','careful@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Defence\n➖ Stats Decrease - Sp.Attack')

@app.message(command=['gentle','gentle@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Defence\n➖ Stats Decrease - Defence')

@app.on_message(command=['sassy','sassy@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Sp.Defence\n➖ Stats Decrease - Speed')

@app.on_message(command=['relaxed','relaxed@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Defence\n➖ Stats Decrease - Speed')

@app.on_message(command=['bold','bold@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Defence\n➖ Stats Decrease - Attack')


@app.on_message(command=['impish','impish@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    bot.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Defence\n➖ Stats Decrease - Sp.Attack')


@app.on_message(command=['lax','lax@pokedexkingbot'])
def nature(message):
    a = message.text[1:]
    a = a[0].upper() + a[1:]
    app.send_message(message.chat.id,f'✨ Info of {a} ✨\n\n➖ Stats Increase - Defence\n➖ Stats Decrease - Sp.Defence')

@app.on_message(command=['pokeballs','pokeballs@pokedexkingbot'])
def pokeballs(message):
    app.reply_to(message,'These poke balls have different catch rate multipliers and can increase the chance of catching certain pokemon\n\n• Regular Ball - Multiplier: x1\n\n• Great Ball - Multiplier: x1.5\n\n• Ultra Ball - Multiplier: x2\n\n• Level Ball - Multiplier: x8 if your pokemon\'s level is quadruple or more of the wild pokemon, x4 if your pokemon\'s level is double or more of the wild pokemon, x2 if your pokemon\'s level is higher than the wild pokemon, x1 otherwise\n\n• Fast Ball - Multiplier: x4 if the wild pokemon\'s base speed is at least 100 (or if it is a magnemite, grimer, or tangela), x1 otherwise\n\n• Repeat Ball - Multiplier: x3.5 if you have previously caught the wild pokemon, x1 otherwise\n\n• Nest Ball - Multiplier: Works better on low level pokemon, (maximum of x4 for very low level)\n\n• Net Ball - Multiplier: x3.5 if the wild pokemon is a water or bug type, x1 otherwise\n\n• Quick Ball - Multiplier: x5 if used in the first turn of the battle, x1 otherwise\n\n• Master Ball - Multiplier: x255 (100% capture guaranteed)\n\n• Safari Ball -Multiplier: x1.5 (only used in the /safari zone)\nTo use a poke ball, click the \'Poke Balls\' option in a wild pokemon battle')

@app.on_message(command=['normal'])
def type(message):
    app.reply_to(message,'Type  :  normal 🐾\n\nStrong Against:\nNone\n\nWeak Against:\nRock, Ghost, Steel\nResistant To:\nGhost\n\nVulnerable To:\nFighting')

@app.on_message(command=['fighting'])
def type(message):
    app.reply_to(message,'Type  :  fighting👊\n\nStrong Against:\nNormal, Rock, Steel, Ice, Dark\n\nWeak Against:\nFlying, Poison, Psychic, Bug, Ghost, Fairy\n\nResistant To:\nRock, Bug, Dark\n\nVulnerable To:\nFlying, Psychic, Fairy')

@app.on_message(command=['rock'])
def type(message):
    app.reply_to(message,'Type  :  rock 🪨🪨\n\nStrong Against:\nFlying, Bug, Fire, Ice\n\nWeak Against:\nFighting, Ground, Steel\n\nResistant To:\nNormal, Flying, Poison, Fire\n\nVulnerable To:\nFighting, Ground, Steel, Water, Grass')

@app.on_message(command=['flying'])
def type(message):
    app.reply_to(message,'Type  :  flying 🦅🦅\n\nStrong Against:\nFighting, Bug, Grass\n\nWeak Against:\nRock, Steel, Electric\n\nResistant To:\nFighting, Ground, Bug, Grass\n\nVulnerable To:\nRock, Electric, Ice')

@app.on_message(command=['poison'])
def type(message):
    app.reply_to(message,'Type  :  poison ☠️\n\nStrong Against:\nGrass, Fairy\n\nWeak Against:\nPoison, Ground, Rock, Ghost, Steel\n\nResistant To:\nFighting, Poison, Grass, Fairy, Bug\n\nVulnerable To:\nGround, Psychic')

ground = '''Type  :  ground 🌏🌏

Strong Against:
Poison, Rock, Steel, Fire, Electric

Weak Against:
Flying, Bug, Grass

Resistant To:
Poison, Rock, Electric

Vulnerable To:
Water, Grass, Ice'''

@app.on_message(command=['ground'])
def type(message):
    app.reply_to(message,ground)

bug = '''Type  :  bug 🐞🐞

Strong Against:
Grass, Psychic, Dark

Weak Against:
Fighting, Flying, Poison, Ghost, Steel, Fire, Fairy

Resistant To:
Fighting, Ground, Grass

Vulnerable To:
Flying, Rock, Fire'''

@app.on_message(command=(['bug'])
def type(message):
    app.reply_to(message,bug)


ghost = '''Type  :  ghost 👻 👻

Strong Against:
Ghost, Psychic

Weak Against:
Normal, Dark

Resistant To:
Normal, Fighting, Poison, Bug

Vulnerable To:
Ghost, Dark'''

@app.on_message(command=['ghost'])
def type(message):
    app.reply_to(message,ghost)

steel = '''Type  :  steel⚙️⚙️

Strong Against:
Rock, Ice, Fairy

Weak Against:
Steel, Fire, Water, Electric

Resistant To:
Normal, Flying, Poison, Rock, Bug, Steel, Grass, Psychic, Ice, Dragon, Fairy

Vulnerable To:
Fighting, Ground, Fire'''

@app.on_message(command=['steel'])
def type(message):
    app.reply_to(message,steel)

fire = '''Type  :  fire🔥🔥

Strong Against:
Bug, Steel, Grass, Ice

Weak Against:
Rock, Fire, Water, Dragon

Resistant To:
Bug, Steel, Fire, Grass, Ice, Fairy

Vulnerable To:
Ground, Rock, Water'''

@app.on_message(command=['fire'])
def type(message):
    app.reply_to(message,fire)

water = '''Type  :  water💧💧

Strong Against:
Ground, Rock, Fire

Weak Against:
Water, Grass, Dragon

Resistant To:
Steel, Fire, Water, Ice

Vulnerable To:
Grass, Electric'''

@app.on_message(command=['water'])
def type(message):
    app.reply_to(message,water)

grass = '''Type  :  grass🌿🌿

Strong Against:
Ground, Rock, Water

Weak Against:
Flying, Poison, Bug, Steel, Fire, Grass, Dragon

Resistant To:
Ground, Water, Grass, Electric

Vulnerable To:
Flying, Poison, Bug, Fire, Ice'''

@app.on_message(command=['grass'])
def type(message):
    app.reply_to(message,grass)


electric = '''Type  :  electric⚡️⚡️

Strong Against:
Flying, Water

Weak Against:
Ground, Grass, Electric, Dragon

Resistant To:
Flying, Steel, Electric

Vulnerable To:
Ground'''
@app.on_message(command=['electric'])
def type(message):
    app.reply_to(message,electric)

psychic = '''Type  :  psychic🔮🔮

Strong Against:
Fighting, Poison

Weak Against:
Steel, Psychic, Dark

Resistant To:
Fighting, Psychic

Vulnerable To:
Bug, Ghost, Dark'''

@app.on_message(command=['psychic'])
def type(message):
    app.reply_to(message,psychic)

ice = '''Type  :  ice 🧊❄️❄️

Strong Against:
Flying, Ground, Grass, Dragon

Weak Against:
Steel, Fire, Water, Ice

Resistant To:
Ice

Vulnerable To:
Fighting, Rock, Steel, Fire'''

@app.on_message(command=['ice'])
def type(message):
    app.reply_to(message,ice)

dragon = '''Type  :  dragon🐉🐉 

Strong Against:
Dragon

Weak Against:
Steel, Fairy

Resistant To:
Fire, Water, Grass, Electric

Vulnerable To:
Ice, Dragon, Fairy'''

@app.on_message(command=['dragon'])
def type(message):
    app.reply_to(message,dragon)

fairy = '''Type  :  fairy🧚‍♂🧚‍♀🧚

Strong Against:
Fighting, Dragon, Dark

Weak Against:
Poison, Steel, Fire

Resistant To:
Fighting, Bug, Dragon, Dark

Vulnerable To:
Poison, Steel'''

@app.on_message(command=['fairy'])
def type(message):
    app.reply_to(message,fairy)

dark = '''Type  :  dark 🕶🌙🌙

Strong Against:
Ghost, Psychic

Weak Against:
Fighting, Dark, Fairy

Resistant To:
Ghost, Psychic, Dark

Vulnerable To:
Fighting, Bug, Fairy'''

@app.on_message(command=['dark'])
def type(message):
    app.reply_to(message,dark)

movesets = '''Moveset For the Commonly used Legendary Trio Pokes and others.

Rayquaza
Dragon Ascent
Earthquake
Outrage
Crunch (can be removed and giga can be added)

Kyogre
Hyper Beam
Water Sprout
Ice beam
Thunderbolt

Groudon
Precipice Blades
Eruption
Rock Slide/Stone edge
Hammer Arm

Dialga
Roar of Time
Flash Cannon
Overheat
Aura Sphere

Palkia
Spacial Rend
Aura Sphere
Hydro Pump
Thunderbolt

Giratina
Shadow Force
Dragon Claw
Earthquake
Giga Impact

Black Kyurem
Freeze Shock
Outrage
Shadow Claw
Fusion Bolt

White Kyurem
Fusion Flare
Dragon Pulse
Ice burn
Focus Blast

Kyurem-Normal
Slash
Outrage
Shadow Claw
Glaciate

Reshiram
Dragon Pulse
Blue Flare
Fusion Flare
Extrasensory

Zekrom
Crunch 
Fusion Bolt
Bolt Strike
Outrage

Yveltal
Foul Play
Rock Slide
Dragon Claw
Sky attack

Xerneas- Spa Trained
Close Combat or Add Focus Blast (optional)
Moonblast
Flash Cannon
Thunderbolt

Atk Trained 
Giga Impact
Close Combat
Moonblast
Megahorn

Zygarde
Earthquake
Rock Slide
Outrage
Crunch

Solgaleo
Sunsteel Strike
Earthquake
Giga Impact
Wild Charge

Lunala
Moongeist Beam
Moonblast
Dream Eater
Hyper Beam

Necrozma-Normal
Prismatic Laser
Rock Blast
Dark Pulse
Photon Geysor

Necrozma-Dusk mane
Rock Blast
Earthquake
Prismatic Laser
Sunsteel Strike

Necrozma-Dawn Wings
Prismatic Laser
Moongeist Beam
Power Gem
Photon Geysor

Necrozma-Ultra
Prismatic Laser
Dark Pulse
Power Gem
Solar Beam /Flash Cannon

Ho-oH
Earthquake
Sky Attack
Sacred Fire
Future Sight (or replace with any tms)

Lugia
Waterfall
Earthquake
Sky Attack
Future Sight

Arceus (Well,it's according to Different types,but Moveset for Normal arc is)

Giga Impact
Earthquake
Rock Slide
Shadow Claw

Zeraora
Plasma Fists
Giga Impact
Brutal Swing
Close Combat

Pheromosa
High Jump Kick
Poison Jab
Giga Impact
Lunge

Mewtwo And Mewtwo Y
Ice Beam(or use blizzard but low accuracy)
Future Sight
Shadow Ball
Aura Sphere(Can be replaced by Focus Blast but risky,as in the case of Ice beam or Blizzard)

Mewtwo X
Giga Impact
Earthquake
Brick Break
Psycho Cut

Victini
V-Create
Zen Headbutt
Wild Charge
Double Edge

Jirachi
Doom Desire
Future Sight
Hyper Beam
Solar Beam

Celebi
Dazzling Gleam
Leaf Storm
Hyper Beam
Future Sight

Regigigas
Giga Impact
Earthquake
Zen Headbutt
Knock off

Deoxys
Psycho Boost
Ice Beam/Blizzard
Thunderbolt/Focus Blast (our choice)
Dark Pulse'''

@app.on_message(command=['moveset'])
def type(message):
    app.reply_to(message,movesets)

@app.on_message(command=['id'])
def id(message):
    app.reply_to(message,""")



# ===== Raid commands =====
@app.on_message(Filters.command(['addcode', 'addcode@pokedexkingBot']))
def call_add_fc(app, message):
    raid.add_fc(app, message, texts)

@app.on_message(Filters.command(['mycode', 'mycode@pokedexkingBot']))
def call_show_my_fc(app, message):
    raid.show_my_fc(app, message, texts)

@app.on_message(Filters.command(['newraid', 'newraid@pokedexkingbot']))
def call_new_raid(app, message):
    raid.new_raid(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'stars' in query.data))
def call_stars(app, message):
    raid.stars(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'join' in query.data))
def call_join(app, message):
    raid.join(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'done' in query.data))
def call_done(app, message):
    raid.done(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'yes' in query.data))
def call_confirm(app, message):
    raid.confirm(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'no' in query.data))
def call_back(app, message):
    raid.back(app, message, texts)

@app.on_callback_query(Filters.create(lambda _, query: 'pin' in query.data))
def call_pin(app, message):
    raid.pin(app, message, texts)


# ===== Presentation =====
@app.on_message(Filters.create(lambda _, message: message.new_chat_members))
def bot_added(app, message):
    for new_member in message.new_chat_members:
        if new_member.id == 1269349088:
            text = texts['added']
            app.send_message(
                chat_id=message.chat.id,
                text=text
            )


app.run()
