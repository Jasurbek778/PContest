from telebot import types
from prettytable import PrettyTable
from functools import partial
import sqlite3
import telebot
import json
import datetime
import random as rand

# Database connection
conn = sqlite3.connect('db.db', check_same_thread=False)
cur = conn.cursor()

token = '7665059273:AAHmcBiMvca1iOAQi4ci2yL9k_G8PjjHFvs'
bot = telebot.TeleBot(token)

last_t = None
ut = 0

reg_m = types.InlineKeyboardMarkup()
reg_m.add(types.InlineKeyboardButton(text='📝 Ro‘yxatdan o‘tish 📝', callback_data='reg'))

home_m = types.InlineKeyboardMarkup(row_width=1)
home_m.add(types.InlineKeyboardButton(text='👤 Profil 👤', callback_data='h_p'))
home_m.add(types.InlineKeyboardButton(text='👥 Foydalanuvchilar 👥', callback_data='h_u'))
home_m.add(types.InlineKeyboardButton(text='💻 Contestlar 💻', callback_data='h_c'))
home_m.add(types.InlineKeyboardButton(text='🧾 Testlar 🧾', callback_data='h_t'))
home_m.add(types.InlineKeyboardButton(text='📘 Botdan foydalanish', callback_data='how_use'))

howuse_m = types.InlineKeyboardMarkup(row_width=1)
howuse_m.add(
    types.InlineKeyboardButton("🧾 Buyruqlar", callback_data='help_cmds'),
    types.InlineKeyboardButton("🧪 Testlar haqida", callback_data='help_tests'),
    types.InlineKeyboardButton("👥 Foydalanuvchi turlari", callback_data='help_users'),
    types.InlineKeyboardButton("🎯 Reyting va Level", callback_data='help_rating'),
    types.InlineKeyboardButton("⬅️ Orqaga", callback_data='b_h')
)



p_m = types.InlineKeyboardMarkup()
p_m.add(types.InlineKeyboardButton(text='💻 Qatnashgan contestlarim 💻', callback_data='p_c'))
p_m.add(types.InlineKeyboardButton(text='🧾 Qatnashgan testlarim 🧾', callback_data='p_t'))
p_m.add(types.InlineKeyboardButton(text='⬅️ Orqaga', callback_data='b_h'))

b_m = types.InlineKeyboardMarkup()
b_m.add(types.InlineKeyboardButton(text='⬅️ Orqaga', callback_data='b_h'))

b_m_adm = types.InlineKeyboardMarkup()
b_m_adm.add(types.InlineKeyboardButton(text='⬅️ Orqaga', callback_data='adm'))

b_m_adm_tests = types.InlineKeyboardMarkup()
b_m_adm_tests.add(types.InlineKeyboardButton(text='⬅️ Orqaga', callback_data='adm_test'))

ad_1 = types.InlineKeyboardMarkup()
ad_1.add(
    types.InlineKeyboardButton(text=' ➕ Yangi test yaratish ➕ ', callback_data='new_t'),
    types.InlineKeyboardButton(text=' ✏️ Mening testlarim ✏️ ', callback_data='my_t'))
ad_1.add(
    types.InlineKeyboardButton(text=" 🔑 Admin/VIP qo'shish 🔑 ", callback_data='new_admin')
)

conf = types.InlineKeyboardMarkup()
conf.add(
    types.InlineKeyboardButton(text='🟢 Yangi test yaratish 🟢', callback_data='new_t_c'),
    types.InlineKeyboardButton(text='⬅ Orqaga', callback_data='adm')
)


def new_rating(p, t):
    m = 64
    s = (t - p) / t
    e = 0.5
    res = int(m*(s - e))
    return res


@bot.message_handler(commands=['start'])
def start_handler(msg):
    global ut
    uid = str(msg.from_user.id)
    cur.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    user = cur.fetchone()
    if user is None:
        bot.send_message(msg.chat.id, 'Assalomu alaykum! PContest botiga xush kelibsiz!', reply_markup=reg_m)
    else:
        ut = int(user[8])
        bot.send_message(msg.chat.id, f'Salom {user[1].split()[1]}! PContest botiga xush kelibsiz.\n 💠 Bosh menyu:\n', parse_mode='Markdown', reply_markup=home_m)

        
@bot.callback_query_handler(func=lambda call: call.data == 'reg')
def register_handler(call):
    msg = bot.send_message(call.message.chat.id, "Ism Familiyangizni kiriting:")
    bot.register_next_step_handler(msg, complete_registration, call.from_user.id)


def complete_registration(msg, user_id):
    full_name = msg.text.strip()
    username = msg.from_user.username or '---'

    cur.execute("""
        INSERT INTO users (fname, uname, uid, rating, level, part_c, part_t, acc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, f"@{username}", str(user_id), 500, 'Pupil', '', '', 0))
    conn.commit()

    bot.send_message(msg.chat.id, "Tabriklaymiz! Ro‘yxatdan o‘tdingiz.")
    
    show_home(msg)


def show_home(msg):
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.send_message(msg.chat.id, "\n💠 Bosh menyu\n", reply_markup=home_m, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'b_h')
def back_to_home(call):
    show_home(call.message)


@bot.message_handler(commands=['adminp'])
def admin_panel(msg):
    global ut
    if ut > 0:
        bot.send_message(msg.chat.id, "\n🔷 Admin Panel\n", reply_markup=ad_1, parse_mode='Markdown')
    else:
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        show_home(msg)


@bot.callback_query_handler(func=lambda call: call.data == 'adm')
def back_adminp(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    global ut
    if ut > 0:
        bot.send_message(call.message.chat.id, "🔷 Admin Panel", reply_markup=ad_1)
    else:
        bot.send_message(call.message.chat.id, "❌ Siz admin emassiz!")
        show_home(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'h_p')
def profile_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    uid = str(call.from_user.id)
    cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    user = cur.fetchone()

    if user:
        t = PrettyTable()
        t.align = 'l'
        t.field_names = [' 👤 Sizning profilingiz', '---']
        t.add_row([' 🆔 Ism', user[1]])
        t.add_row([' 🏆 Rating', user[4]])
        t.add_row([' ⭐️ Level', user[5]])
        t.add_row([' 💻 Qatnashgan contestlari', len(user[6]) if user[6] else 0])
        t.add_row([' 🧾 Qatnashgan testlari', len(user[7]) if user[7] else 0])
        
        bot.send_message(call.message.chat.id, f'```{str(t)}```', reply_markup=p_m, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'h_u')
def users_list(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cur.execute("SELECT fname, rating FROM users")
    users = cur.fetchall()

    t = PrettyTable(['Foydalanuvchi', 'Rating'])
    for name, rating in users:
        t.add_row([name, rating])

    bot.send_message(call.message.chat.id, f"👥 Foydalanuvchilar:\n\n```{t}```", parse_mode='Markdown', reply_markup=b_m)

@bot.callback_query_handler(func=lambda call: call.data == 'p_t')
def my_tests(call):
    uid = str(call.from_user.id)
    cur.execute("SELECT part_t FROM users WHERE uid = ?", (uid,))
    row = cur.fetchone()

    if not row or not row[0]:
        bot.send_message(call.message.chat.id, "❌ Siz hali hech qanday testda qatnashmagansiz.", reply_markup=b_m)
        return

    test_ids = row[0].split()
    t = PrettyTable()
    t.field_names = ['Test nomi', 'Test ID', 'O\'rin', 'Rating']

    for tid in test_ids:
        cur.execute("SELECT tname, ans, res, rated FROM tests WHERE tid = ?", (tid,))
        data = cur.fetchone()
        if not data:
            continue

        tname, cor, res_json, rated = data
        res = json.loads(res_json or '{}')

        users = []
        for pid, ans in res.items():
            sc = sum(1 for i in range(min(len(ans), len(cor))) if ans[i] == cor[i])
            users.append((pid, sc))

        users.sort(key=lambda x: -x[1])
        total = len(users)
        rank = next((i + 1 for i, (pid, _) in enumerate(users) if pid == uid), '?')

        delta = '–'
        if rated == 1:
            cur.execute("SELECT rating FROM users WHERE uid = ?", (uid,))
            urating = cur.fetchone()[0]
            d = new_rating(rank, total)

        t.add_row([tname, tid, rank, f'{d:+}' if isinstance(d, int) else d])

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data='b_h'))
    bot.send_message(call.message.chat.id, f"🧾 Qatnashgan testlaringiz:\n```{t}```", parse_mode='Markdown', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'h_c')
def contests_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Hozircha contest mavjud emas.", reply_markup=b_m)

@bot.callback_query_handler(func=lambda call: call.data == 'enter_test_code')
def ask_for_test_id(call):
    msg = bot.send_message(call.message.chat.id, "🔢 Test ID ni kiriting:")
    bot.register_next_step_handler(msg, find_and_join_test, call)

def find_and_join_test(msg, call):
    uid = str(msg.from_user.id)
    try:
        tid = int(msg.text.strip())
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Test ID no`to`gri kiritilgan.")
        my_tests(call)
        return

    cur.execute("SELECT res, ans, state FROM tests WHERE tid = ?", (tid,))
    row = cur.fetchone()

    if not row:
        bot.send_message(msg.chat.id, "❌ Bunday IDli test topilmadi.")
        my_tests(call)
        return

    res_json, cor, state = row
    if state != 1:
        status = "hali boshlanmagan" if state == 0 else "allaqachon tugagan"
        bot.send_message(msg.chat.id, f"⛔ Bu test {status}.")
        return

    try:
        res = json.loads(res_json or '{}')
    except (json.JSONDecodeError, TypeError):
        res = {}

    if uid in res:
        bot.send_message(msg.chat.id, "⚠️ Siz bu testda allaqachon qatnashgansiz.")
        return

    msg = bot.send_message(msg.chat.id, "Test javoblarini quyidagi ko'rinishda kiriting: ABCDEABCDE yoki abcdeabcde")
    bot.register_next_step_handler(msg, partial(save_test_answer, tid=tid, uid=uid, cor=cor, attempt=1))

@bot.callback_query_handler(func=lambda call: call.data == 'h_t')
def tests_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

    cur.execute("SELECT tname, tid, state FROM tests WHERE rated = 1")
    tests = cur.fetchall()

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(text=" 🆔 Test ID orqali kirish 🆔 ", callback_data="enter_test_code"))

    t = PrettyTable()
    t.field_names = ['Test nomi', 'Test ID', 'Holat']

    for tname, tid, state in tests:
        t.add_row([tname, tid, state])
        kb.add(types.InlineKeyboardButton(text=f"{tname} ({tid})", callback_data=f"join_test_{tid}"))

    kb.add(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data='b_h'))

    if not tests:
        bot.send_message(call.message.chat.id, "⛔ Hozircha rated testlar mavjud emas.", reply_markup=kb)
        return

    bot.send_message(call.message.chat.id, f" 🧾 Rated testlar ro‘yxati:\n ```{str(t)}```", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('join_test_'))
def join_test(call):
    tid = int(call.data.split('_')[2])
    uid = str(call.from_user.id)

    cur.execute("SELECT res, ans, state FROM tests WHERE tid = ?", (tid,))
    row = cur.fetchone()

    res_json, cor, state = row

    if state == 1:
        try:
            res = json.loads(res_json)
        except (json.JSONDecodeError, TypeError):
            res = {}

        if uid in res:
            bot.send_message(call.message.chat.id, "⚠️ Siz bu testda qatnashgansiz.")
            return

        msg = bot.send_message(call.message.chat.id, "Test javoblarini quyidagi ko'rinishda kiriting: ABCDEABCDE yoki abcdeabcde")
        bot.register_next_step_handler(msg, partial(save_test_answer, tid=tid, uid=uid, cor=cor, attempt=1))

    elif state == 2:
        bot.send_message(call.message.chat.id, " 🛑 Bu test allaqachon tugagan")
    else:
        bot.send_message(call.message.chat.id, " 🚫 Bu test hali boshlanmagan.")

def save_test_answer(msg, tid, uid, cor, attempt=1):
    ans = msg.text.strip().upper()
    w = 0
    if not ans.isalpha() or len(ans) != len(cor):
        if attempt < 5:
            w = 1
            warning = f" ❌ Test kalitlari soni {len(correct)} ta. Test javoblarni qaytadan kiriting:" if len(ans) != len(cor) else f" ❌ Test kalitlarini quyidagi ko`rinishda kiriting: ABCDEABCDE yoki abcdeabcde"
            retry_msg = bot.send_message(msg.chat.id, warning)
            bot.register_next_step_handler(retry_msg, partial(save_test_answer, tid=tid, uid=uid, cor=cor, attempt=attempt + 1))
        else:
            show_home(call.message)
    if w: return
    cur.execute("SELECT res FROM tests WHERE tid = ?", (tid,))
    res_json = cur.fetchone()[0]
    try:
        res = json.loads(res_json) if res_json and res_json.strip() else {}
    except json.JSONDecodeError:
        res = {}
    if uid in res:
        bot.send_message(msg.chat.id, "⚠️ Siz bu testda allaqachon qatnashgansiz.")
        show_home(msg)
        return
    
    res[uid] = ans
    cur.execute("UPDATE tests SET res = ? WHERE tid = ?", (json.dumps(res), tid))

    cur.execute("SELECT part_t FROM users WHERE uid = ?", (uid,))
    pp = cur.fetchone()[0] or ''
    np = pp.split() + [str(tid)]
    cur.execute("UPDATE users SET part_t = ? WHERE uid = ?", (' '.join(np), uid))
    conn.commit()

    sc = sum(1 for i in range(len(cor)) if ans[i] == cor[i])
    bot.send_message(msg.chat.id, f" ✅ Javoblaringiz qabul qilindi. Natija test tugaganidan so'ng e'lon qilinadi.")
    show_home(msg)


@bot.callback_query_handler(func=lambda call: call.data == 'new_t')
def new_test_init(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "➕ Yangi test yaratish", reply_markup=conf)


@bot.callback_query_handler(func=lambda call: call.data == 'new_t_c')
def new_test_name(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = bot.send_message(call.message.chat.id, "Test nomini kiriting:")
    bot.register_next_step_handler(msg, ask_rated, call.from_user.id)

def ask_rated(msg, uid):
    tname = msg.text.strip()
    kb = types.InlineKeyboardMarkup()
    if ut > 1: kb.add(types.InlineKeyboardButton("✅ Rated", callback_data=f"rated_yes_{tname}"))
    kb.add(types.InlineKeyboardButton("❌ Unrated", callback_data=f"rated_no_{tname}"))
    bot.send_message(msg.chat.id, "\n Test turi:\n", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rated_"))
def choose_rated(call):
    parts = call.data.split('_')
    rated = 1 if parts[1] == 'yes' else 0
    tname = '_'.join(parts[2:])
    msg = bot.send_message(call.message.chat.id, "Test kalitlarini kiriting (masalan: ABCDE):")
    bot.register_next_step_handler(msg, finalize_test, tname, call.from_user.id, rated)


def finalize_test(msg, tname, user_id, rated):
    bot.delete_message(msg.chat.id, msg.message_id)
    answers = msg.text.strip()
    tid = rand.randint(1000, 99999)

    cur.execute("SELECT tid FROM tests")
    existing_ids = [r[0] for r in cur.fetchall()]
    while tid in existing_ids:
        tid = rand.randint(1000, 99999)

    cur.execute("""
        INSERT INTO tests (tname, tid, time, ans, res, cr, state, rated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tname, tid, str(datetime.datetime.now()).split()[0], answers, '{}', str(user_id), 0, rated))
    conn.commit()

    bot.send_message(msg.chat.id, "✅ Test yaratildi!")
    admin_panel(msg)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_test_'))
def edit_test_panel(call):
    last_t = call
    bot.delete_message(call.message.chat.id, call.message.message_id)
    tid = int(call.data.split('_')[2])
    cur.execute("SELECT tname, state, rated FROM tests WHERE tid = ?", (tid,))
    row = cur.fetchone()

    if not row:
        bot.send_message(call.message.chat.id, "❌ Test topilmadi.")
        return

    tname, state, rated = row
    status = "⏳ Boshlanmagan" if state == 0 else "🟢 O‘tkazilmoqda" if state == 1 else "🔴 Tugagan"
    text = f"""
📝 *Test nomi:* {tname}
🆔 *Test ID:* `{tid}`
📌 *Holati:* {status}
🔷 *Test turi:* {'Rated' if rated else 'Unrated'}
    """

    kb = types.InlineKeyboardMarkup()
    if state == 0:
        kb.add(types.InlineKeyboardButton("▶️ Testni boshlash", callback_data=f'start_test_{tid}'))
    elif state == 1:
        kb.add(types.InlineKeyboardButton("⛔ Testni tugatish", callback_data=f'end_test_{tid}'))

    kb.add(
        types.InlineKeyboardButton("📊 Natijalarni ko‘rish", callback_data=f'see_result_{tid}'),
        types.InlineKeyboardButton("❌ Testni o‘chirish", callback_data=f'del_test_{tid}')
    )
    kb.add(types.InlineKeyboardButton("⬅️ Orqaga", callback_data='my_t'))

    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == 'adm_test')
def back_test(call):
    edit_test_panel(last_t)

@bot.callback_query_handler(func=lambda call: call.data == 'my_t')
def all_tests_list(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cur.execute("SELECT tname, tid, state, rated FROM tests")
    tests = cur.fetchall()

    if not tests:
        bot.send_message(call.message.chat.id, "❌ Hozircha testlar mavjud emas.", reply_markup=b_m_adm)
        return

    text = "\n 🧾 Yaratilgan testlar ro‘yxati:\n"
    kb = types.InlineKeyboardMarkup(row_width=2)

    t = PrettyTable()
    t.align = 'l'
    t.field_names = ['Test', 'Test ID', 'Holat', 'Test turi']
    for tname, tid, state, rated in tests:
        status = "⚪️ Boshlanmagan" if state == 0 else "🟢 O‘tkazilmoqda" if state == 1 else "🔴 Tugagan"
        rated = 'Rated' if rated else 'Unrated'
        t.add_row([tname, tid, status, rated])
        kb.add(types.InlineKeyboardButton(text=str(tid), callback_data=f'edit_test_{tid}'))

    kb.add(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data='adm'))

    bot.send_message(call.message.chat.id, f' 🧾 Mening testlarim:\n\n ```{str(t)}```', reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('start_test_'))
def start_test(call):
    tid = int(call.data.split('_')[2])
    cur.execute("UPDATE tests SET state = 1 WHERE tid = ?", (tid,))
    conn.commit()
    bot.send_message(call.message.chat.id, f"✅ Test `{tid}` boshlandi.", parse_mode='Markdown')
    edit_test_panel(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('end_test_'))
def end_test(call):
    tid = int(call.data.split('_')[2])
    cur.execute("UPDATE tests SET state = 2 WHERE tid = ?", (tid,))
    conn.commit()
    bot.send_message(call.message.chat.id, f"⛔ Test `{tid}` tugatildi.", parse_mode='Markdown')
    edit_test_panel(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('see_result_'))
def see_test_results(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    tid = int(call.data.split('_')[2])
    
    cur.execute("SELECT res, ans, rated FROM tests WHERE tid = ?", (tid,))
    row = cur.fetchone()
    if not row:
        bot.send_message(call.message.chat.id, "❌ Test topilmadi.")
        return

    res_json, cor, rated = row
    res = json.loads(res_json or '{}')

    if not res:
        bot.send_message(call.message.chat.id, "❌ Bu testda hech kim qatnashmadi.", reply_markup=b_m_adm_tests)
        return
    
    ress = []
    for uid, ans in res.items():
        score = sum(1 for i in range(min(len(ans), len(cor))) if ans[i] == cor[i])
        cur.execute("SELECT fname, rating FROM users WHERE uid = ?", (uid,))
        user = cur.fetchone()
        name = user[0] if user else "-- Unknown --"
        rating = user[1]
        ress.append({'uid': uid, 'name': name, 'score': score, 'rating': rating})
    
    ress.sort(key=lambda x: -x['score'])
    
    total = len(ress)
    t = PrettyTable()
    t.field_names = ['Foydalanuvchi', 'Ball', 'Reyting', 'Change']

    for i, user in enumerate(ress):
        uid = user['uid']
        orating = user['rating']
        rank = i + 1

        if rated == 1:
            ch = new_rating(rank, total)
            nrating = orating + ch
            cur.execute("UPDATE users SET rating = ? WHERE uid = ?", ('+'+str(nrating) if nrating > 0 else str(nrating), uid))
        else:
            ch = " --- "

        t.add_row([user['name'], user['score'], user['rating'], ch])

    conn.commit()
    bot.send_message(call.message.chat.id, f' 📊 {tid} - Test natijalari:\n```{t}```', parse_mode='Markdown', reply_markup=b_m_adm_tests)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_test_'))
def delete_test(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    tid = call.data.split('_')[2]

    
    
    cur.execute('delete from tests where tid = ?', (tid,))
    conn.commit()
    bot.send_message(call.message.chat.id, " ✅ Test muvaffaqiyatli o'chirildi.", reply_markup=b_m_adm_tests)

@bot.callback_query_handler(func=lambda call: call.data == 'how_use')
def how_use_menu(call):
    bot.send_message(call.message.chat.id, "📘 Botdan foydalanish haqida bo‘limni tanlang:", reply_markup=howuse_m)


@bot.callback_query_handler(func=lambda call: call.data == 'help_cmds')
def help_cmds(call):
    text = """
🧾 *Bot buyruqlari:*

/start – Botni qayta ishga tushirish 
/help – Botdan foydalanish tartibi
/adminp – Admin panel (faqat adminlar uchun)  

⚠️ Ko‘pgina funksiyalar menyular orqali amalga oshiriladi.
"""
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=howuse_m)

@bot.callback_query_handler(func=lambda call: call.data == 'help_tests')
def help_tests(call):
    text = """
🧪 *Testlar haqida:*

– `Rated` testlar: Testda ko'rsatgan natijaga ko'ra ko'tariladi yoki tushadi.  
– `Unrated` testlar: Faqatgina Test ID orqali kirish mumkin. Reyting va Levelga hech qanday ta'sir ko'rsatmaydi.

– Test istalgan vaqtda Adminlar tomonidan boshlanib, tugashi mumkin.
– Test holati testlar ko'rsatiladigan ro'yxatga ko'ra aniqlash mumkin:
    - ⚪️ Boshlanmagan
    - 🟢 O‘tkazilmoqda
    - 🔴 Tugagan

– Test javoblarini faqatgina test o'tkazilayotgan paytda kiritish mumkin.
– Test natijalari test tugagandan so'ng Adminlar tomonidan barchaga e'lon qilinadi.
"""
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=howuse_m)

@bot.callback_query_handler(func=lambda call: call.data == 'help_users')
def help_users(call):
    text = """
 👥 *Foydalanuvchi turlari:*

 👤 `User` – Faqat testlarda ishtirok etish huquqiga ega.
 💎 `VIP` – Faqat Unrated testlar yaratishi huquqiga ega.
 🔧 `Admin` – Har qanday turdagi testlarni yaratish va boshqarish.
 👑 `Creator` – Barcha huquqlarga ega.

 ⚠️ Admin/creator huquqlari faqat maxsus tasdiqlangan foydalanuvchilarda bo‘ladi. VIP/Adminga ruxsat olish uchun biz bilan bog'laning: @IlhomovJasurbek.
"""
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=howuse_m)

@bot.callback_query_handler(func=lambda call: call.data == 'help_rating')
def help_rating(call):
    text = """
🎯 *Reyting va Level tizimi:*

`0–500` — 🟤 Noob
`500–600` — ⚪️ Pupil
`600–900` — 🟡 Advanced
`900–1200` — 🟠 Expert
`1200–1600` — 🟢 Pro
`1600–200` — 🔴 Master
`2000–2500` — 🔵 Pro Master
`2500–3000` — 🟣 Grandmaster 
`3000+` — ⚫️ Hacker  

🏆 Reyting va Level faqatgina *Rated* testlarda ko'rsatgan natijalarga qarab adminlar tomonidan ko'tariladi yoki tushiriladi.
"""
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=howuse_m)

@bot.callback_query_handler(func=lambda call: call.data == 'new_admin')
def make_admin_handler(msg):
    uid = str(msg.from_user.id)
    cur.execute("SELECT acc FROM users WHERE uid = ?", (uid,))
    row = cur.fetchone()
    if not row or row[0] != 3:
        bot.send_message(msg.chat.id, "❌ Faqat Creator yangi admin yoki VIP yaratishi mumkin.")
        return

    bot.send_message(msg.chat.id, "🆔 Foydalanuvchi ID sini kiriting:")
    bot.register_next_step_handler(msg, ask_new_role)

def ask_new_role(msg):
    try:
        target_uid = msg.text.strip()
        cur.execute("SELECT fname FROM users WHERE uid = ?", (target_uid,))
        if not cur.fetchone():
            bot.send_message(msg.chat.id, "❌ Bu ID bo‘yicha foydalanuvchi topilmadi.", reply_markup=b_m_adm)
            return

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔧 Admin 🔧", callback_data=f"set_admin_{target_uid}"))
        kb.add(types.InlineKeyboardButton("💎 VIP 💎", callback_data=f"set_vip_{target_uid}"))

        bot.send_message(msg.chat.id, "Adminlik turini tanlang:\n", reply_markup=kb)
    except Exception as e:
        bot.send_message(msg.chat.id, f"Xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_admin_') or call.data.startswith('set_vip_'))
def set_access_role(call):
    creator_uid = str(call.from_user.id)
    cur.execute("SELECT acc FROM users WHERE uid = ?", (creator_uid,))
    row = cur.fetchone()
    if not row or row[0] != 3:
        bot.send_message(call.message.chat.id, "❌ Faqat Creatorgina Admin/VIP qila oladi.", reply_markup=b_m_adm)
        return

    parts = call.data.split('_')
    role = parts[1]
    target_uid = parts[2]

    new_acc = 2 if role == 'admin' else 1
    cur.execute("UPDATE users SET acc = ? WHERE uid = ?", (new_acc, target_uid))
    conn.commit()

    bot.send_message(call.message.chat.id, f" ✅ Foydalanuvchi - {target_uid} muvaffaqiyatli {'Admin' if new_acc == 2 else 'VIP'} qilindi.")
    admin_panel(call.message)

bot.polling(none_stop=True)
conn.close()
