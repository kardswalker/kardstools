import requests
import json
import sys
import certifi
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning
import warnings
#import curses


def safe_post(url, **kwargs):
    """Try requests.post with certifi CA bundle first, then fallback to verify=False and suppress warnings."""
    try:
        kwargs.setdefault('verify', certifi.where())
        return requests.post(url, **kwargs)
    except SSLError:
        warnings.simplefilter('ignore', InsecureRequestWarning)
        kwargs['verify'] = False
        return requests.post(url, **kwargs)


def safe_get(url, **kwargs):
    """Try requests.get with certifi CA bundle first, then fallback to verify=False and suppress warnings."""
    try:
        kwargs.setdefault('verify', certifi.where())
        return requests.get(url, **kwargs)
    except SSLError:
        warnings.simplefilter('ignore', InsecureRequestWarning)
        kwargs['verify'] = False
        return requests.get(url, **kwargs)


def safe_put(url, **kwargs):
    """Try requests.put with certifi CA bundle first, then fallback to verify=False and suppress warnings."""
    try:
        kwargs.setdefault('verify', certifi.where())
        return requests.put(url, **kwargs)
    except SSLError:
        warnings.simplefilter('ignore', InsecureRequestWarning)
        kwargs['verify'] = False
        return requests.put(url, **kwargs)


default_headers = {
    'Host': 'kards.live.1939api.com',
    'Accept-Encoding': 'deflate, gzip',
    'Accept': 'application/json',
    'X-Api-Key': '1939-kards-5dcda429f:Kards 1.46.24673.launcher',
    'Drift-Api-Key': '1939-kards-5dcda429f:Kards 1.46.24673.launcher',
    'Content-Type': 'application/json',
    'User-Agent': 'kards/++UE5+Release-5.6-CL-44394996 (http-eventloop) Windows/10.0.22000.1.256.64bit'
}

with open('config.json', 'r') as f:
    config = json.load(f)
    JWT = config.get('jwt', '')
    uid = config.get('uid', '')
    pid = config.get('pid', '')

headers_auth = None
if JWT:
    headers_auth = dict(default_headers)
    headers_auth['Authorization'] = f'JWT {JWT}'

print("Kards Tools v0.1")
if JWT == '' or uid == '' or pid == '':
    print("账号设置有误，请输入账号密码以登录。")
    print("请输入账号：")
    username = input()
    print("请输入密码：")
    password = input()
    def safe_post(url, **kwargs):
        """Try requests.post with certifi CA bundle first, then fallback to verify=False and suppress warnings."""
        try:
            # prefer explicit certifi bundle
            kwargs.setdefault('verify', certifi.where())
            return requests.post(url, **kwargs)
        except SSLError:
            # fallback: disable verification but suppress warnings
            warnings.simplefilter('ignore', InsecureRequestWarning)
            kwargs['verify'] = False
            return requests.post(url, **kwargs)

    def safe_get(url, **kwargs):
        """Try requests.get with certifi CA bundle first, then fallback to verify=False and suppress warnings."""
        try:
            kwargs.setdefault('verify', certifi.where())
            return requests.get(url, **kwargs)
        except SSLError:
            warnings.simplefilter('ignore', InsecureRequestWarning)
            kwargs['verify'] = False
            return requests.get(url, **kwargs)

    default_headers = {
        'Host': 'kards.live.1939api.com',
        'Accept-Encoding': 'deflate, gzip',
        'Accept': 'application/json',
        'X-Api-Key': '1939-kards-5dcda429f:Kards 1.46.24673.launcher',
        'Drift-Api-Key': '1939-kards-5dcda429f:Kards 1.46.24673.launcher',
        'Content-Type': 'application/json',
        'User-Agent': 'kards/++UE5+Release-5.6-CL-44394996 (http-eventloop) Windows/10.0.22000.1.256.64bit'
    }

    login = safe_post('https://kards.live.1939api.com/session', headers=default_headers, json={
  "provider": "device_id",
  "provider_details": {
    "payment_provider": "XSOLLA"
  },
  "client_type": "UE5",
  "build": "Kards 1.46.24673.launcher",
  "platform_type": "Windows",
  "app_guid": "Kards",
  "version": "Kards 1.46.24673.launcher",
  "platform_info": "{\r\n\t\"device_profile\": \"Windows\",\r\n\t\"cpu_vendor\": \"GenuineIntel\",\r\n\t\"cpu_brand\": \"      Intel(R) Xeon(R) CPU E5-2680 v2 @ 2.80GHz\",\r\n\t\"gpu_brand\": \"NVIDIA GeForce GTX 1060 6GB\",\r\n\t\"num_cores_physical\": 10,\r\n\t\"num_cores_logical\": 20,\r\n\t\"physical_memory_gb\": 16,\r\n\t\"hash\": \"4d74228ed8d8db8684cc5817ab7d12b10d3decc6b4f16b8756\",\r\n\t\"locale\": \"zh-CN\"\r\n}",
  "platform_version": "Windows 11 (21H2) [10.0.22000.2538] ",
  "account_linking": "{\r\n\t\"username\": \"" + username + "\",\r\n\t\"password\": \"" + password + "\"\r\n}",
  "language": "zh-Hans",
  "automatic_account_creation": True,
  "username": "device:Windows-41DD4DDEC8B8A9BB1E7653AE",
  "password": "536EC7499F07C51A8E"
})
    # check login response
    if not login.ok:
        print(f"Login request failed: {login.status_code} {login.text}")
        sys.exit(1)

    try:
        login_data = login.json()
    except ValueError:
        print(f"Login response is not valid JSON: {login.text}")
        sys.exit(1)

    JWT = login_data.get('jwt')
    if not JWT:
        print(f"'jwt' not found in login response: {login_data}")
        sys.exit(1)

    # use GET to validate auth and retrieve current_user
    headers_auth = dict(default_headers)
    headers_auth['Authorization'] = f'JWT {JWT}'
    try:
        login2 = safe_get('https://kards.live.1939api.com', headers=headers_auth)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    if not login2.ok:
        print(f"Auth check failed: {login2.status_code} {login2.text}")
        sys.exit(1)

    try:
        login2_data = login2.json()
    except ValueError:
        print(f"Auth response is not valid JSON: {login2.text}")
        sys.exit(1)

    current_user = login2_data.get('current_user', {})
    uid = current_user.get('user_id')
    pid = current_user.get('player_id')
    if not uid or not pid:
        print(f"Missing user/player id in auth response: {login2_data}")
        sys.exit(1)
    with open('config.json', 'w') as f:
        json.dump({
            'jwt': JWT,
            'uid': uid,
            'pid': pid
        }, f)

    print("已将账号保存至config.json")

print("\033[34m欢迎使用Kards工具箱！\033[0m")
print("\033[31m本脚本完全免费，禁止倒卖！\033[0m")
print("Kards Mod学习交流群：587649083")
print("1.一键完成每日任务")
print("2.退出登录")
print("3.改名")
print("4.更换头像(可更换未拥有头像)")
print("5.更换卡背")
print("6.更换总部")
print("7.一键完成成就")
print("0.退出")
choice = input("请选择：")
choice = choice.strip()
if choice == "1":
    missions = safe_get(f'https://kards.live.1939api.com/players/{pid}/dailymissions', headers=headers_auth)
    if not missions.ok:
        print(f"获取任务失败！")
        sys.exit(1)
    else:
        for mission in missions.json().get('missions', []):
            safe_put(f'https://kards.live.1939api.com/players/{pid}/dailymissions', headers=headers_auth, json={"action":"finish","id": mission.get("id")})
            print(f'任务 {mission.get("mission_id")} 已完成！')
            exit(0)
elif choice == "2":  
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        config['jwt'] = ''
        config['uid'] = ''
        config['pid'] = ''
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("已退出登录。")
elif choice == "0":
    sys.exit(0)
elif choice == "3":
    new_name = input("请输入新的名字：")
    safe_put(f'https://kards.live.1939api.com/players/{pid}', headers=headers_auth, json={"action": "set-name", "value": new_name})
    print("改名请求已发送。")
elif choice == "4":
    # 读取 avatars.json 并支持多种结构（DataTable -> Rows 或 普通列表）
    with open('avatars.json', 'r', encoding='utf-8') as f:
        avatars_raw = json.load(f)

    candidates = []
    # DataTable case: top-level是列表，第一项的 Rows 包含键->属性
    if isinstance(avatars_raw, list) and len(avatars_raw) > 0 and 'Rows' in avatars_raw[0]:
        rows = avatars_raw[0].get('Rows', {})
        for key, val in rows.items():
            # 尝试解析显示名字段
            display = None
            # some entries have displayName_... with LocalizedString
            for k2, v2 in val.items():
                if k2.startswith('displayName') and isinstance(v2, dict):
                    display = v2.get('LocalizedString') or v2.get('CultureInvariantString')
                    break
            candidates.append({'key': key, 'name': display or key})
    # Simple array/object case
    elif isinstance(avatars_raw, dict):
        # 如果 avatars.json 是字典直接存 rows
        rows = avatars_raw.get('avatars') or avatars_raw
        if isinstance(rows, dict):
            for key, val in rows.items():
                name = val.get('displayName') if isinstance(val, dict) else None
                candidates.append({'key': key, 'name': name or key})
        elif isinstance(rows, list):
            for entry in rows:
                # expect entry to have 'id' and 'name' or similar
                key = entry.get('id') or entry.get('key') or entry.get('name')
                name = entry.get('name') or entry.get('displayName') or key
                candidates.append({'key': key, 'name': name})
    elif isinstance(avatars_raw, list):
        # best-effort: list of simple entries
        for entry in avatars_raw:
            if isinstance(entry, dict):
                key = entry.get('id') or entry.get('key') or entry.get('name')
                name = entry.get('name') or entry.get('displayName') or key
                candidates.append({'key': key, 'name': name})

    if not candidates:
        print('未能解析到可用头像，请检查 avatars.json 格式。')
    else:
        print('可用头像：')
        for idx, c in enumerate(candidates, start=1):
            print(f"{idx}. key={c['key']}  名称={c['name']}")

        sel = input('请输入要更换的头像编号或 key：').strip()
        chosen = None
        if sel.isdigit():
            i = int(sel) - 1
            if 0 <= i < len(candidates):
                chosen = candidates[i]
        else:
            for c in candidates:
                if c['key'] == sel:
                    chosen = c
                    break

        if not chosen:
            print('选择无效，已取消。')
        else:
            item_id = chosen['key']
            print(f'正在发送更换头像请求：{item_id} ({chosen["name"]})')
            resp = safe_post(f'https://kards.live.1939api.com/items/{pid}', headers=headers_auth, json={"item_id": item_id, "slot": "avatar", "faction": "NotAvailable"})
            if resp is None:
                print('请求没有返回。')
            elif not getattr(resp, 'ok', False):
                print(f'更换头像失败: {getattr(resp, "status_code", "?")} {getattr(resp, "text", "")}')
            else:
                print('头像更换成功。')
elif choice == "5":
    # 获取玩家卡组
    resp = safe_get(f'https://kards.live.1939api.com/players/{pid}/decks', headers=headers_auth)
    if not resp or not getattr(resp, 'ok', False):
        print('获取卡组失败。')
        sys.exit(1)
    decks = resp.json()
    # decks 有可能是列表或 {'decks': [...]}
    if isinstance(decks, dict) and 'decks' in decks:
        deck_list = decks.get('decks', [])
    elif isinstance(decks, list):
        deck_list = decks
    else:
        print('无法解析卡组响应')
        sys.exit(1)

    if not deck_list:
        print('未找到卡组。')
        sys.exit(1)

    print('你的卡组：')
    for i, d in enumerate(deck_list, start=1):
        print(f"{i}. id={d.get('id')} name={d.get('name')} main_faction={d.get('main_faction')} card_back={d.get('card_back')}")

    sel = input('请输入要修改卡背的卡组编号或 id：').strip()
    chosen_deck = None
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(deck_list):
            chosen_deck = deck_list[idx]
    else:
        for d in deck_list:
            if str(d.get('id')) == sel:
                chosen_deck = d
                break

    if not chosen_deck:
        print('选择无效，已取消。')
        sys.exit(0)

    # 优先读取 Data/cardbacks 目录内的文件名作为可选卡背（去掉扩展名）
    cardbacks = []
    try:
        import os
        cb_dir = os.path.join('Data', 'cardbacks')
        if os.path.isdir(cb_dir):
            for fname in sorted(os.listdir(cb_dir)):
                if not fname or fname.startswith('.'):
                    continue
                key = os.path.splitext(fname)[0]
                cardbacks.append({'key': key, 'name': key})
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        # fallback: 读取 Data/cardbacks.json 或从卡组中收集现有 card_back
        try:
            with open('Data/cardbacks.json', 'r', encoding='utf-8') as f:
                cb_raw = json.load(f)
                # 支持多种结构：list/dict
                if isinstance(cb_raw, dict):
                    candidates = cb_raw.get('cardbacks') or cb_raw.get('Data') or cb_raw
                    if isinstance(candidates, dict):
                        for k, v in candidates.items():
                            name = v.get('displayName') if isinstance(v, dict) else None
                            cardbacks.append({'key': k, 'name': name or k})
                    elif isinstance(candidates, list):
                        for entry in candidates:
                            if isinstance(entry, dict):
                                key = entry.get('id') or entry.get('key') or entry.get('name')
                                name = entry.get('name') or entry.get('displayName') or key
                                cardbacks.append({'key': key, 'name': name})
                elif isinstance(cb_raw, list):
                    for entry in cb_raw:
                        if isinstance(entry, dict):
                            key = entry.get('id') or entry.get('key') or entry.get('name')
                            name = entry.get('name') or entry.get('displayName') or key
                            cardbacks.append({'key': key, 'name': name})
        except FileNotFoundError:
            # 最后回退: collect unique card_back from player's decks
            seen = set()
            for d in deck_list:
                cb = d.get('card_back')
                if cb and cb not in seen:
                    seen.add(cb)
                    cardbacks.append({'key': cb, 'name': cb})

    if not cardbacks:
        print('未能找到可用的卡背。')
        sys.exit(1)

    print('可用卡背：')
    for i, cb in enumerate(cardbacks, start=1):
        print(f"{i}. key={cb['key']} 名称={cb['name']}")

    sel_cb = input('请输入卡背编号或 key：').strip()
    chosen_cb = None
    if sel_cb.isdigit():
        idx = int(sel_cb) - 1
        if 0 <= idx < len(cardbacks):
            chosen_cb = cardbacks[idx]
    else:
        for cb in cardbacks:
            if cb['key'] == sel_cb:
                chosen_cb = cb
                break

    if not chosen_cb:
        print('卡背选择无效，已取消。')
        sys.exit(0)

    deck_id = chosen_deck.get('id')
    card_back_key = chosen_cb['key']
    print(f'正在将卡组 {deck_id} 的卡背更换为 {card_back_key} ...')
    put_resp = safe_put(f'https://kards.live.1939api.com/players/{pid}/decks', headers=headers_auth, json={
        'action': 'change_card_back',
        'id': deck_id,
        'name': card_back_key
    })
    if not put_resp or not getattr(put_resp, 'ok', False):
        print(f'更换卡背失败: {getattr(put_resp, "status_code", "?")} {getattr(put_resp, "text", "")})')
    else:
        print('卡背更换成功。')
elif choice == "6":
    # 更换总部：先获取玩家卡组，选择卡组后选择总部并发送 PUT
    resp = safe_get(f'https://kards.live.1939api.com/players/{pid}/decks', headers=headers_auth)
    if not resp or not getattr(resp, 'ok', False):
        print('获取卡组失败，无法更换总部。')
        sys.exit(1)
    decks_payload = resp.json()
    if isinstance(decks_payload, dict) and 'decks' in decks_payload:
        deck_list = decks_payload.get('decks', [])
    elif isinstance(decks_payload, list):
        deck_list = decks_payload
    else:
        print('无法解析卡组响应')
        sys.exit(1)

    if not deck_list:
        print('未找到卡组，无法更换总部。')
        sys.exit(1)

    print('你的卡组：')
    for i, d in enumerate(deck_list, start=1):
        print(f"{i}. id={d.get('id')} name={d.get('name')} main_faction={d.get('main_faction')} card_back={d.get('card_back')}")

    sel = input('请输入要修改总部的卡组编号或 id：').strip()
    chosen_deck = None
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(deck_list):
            chosen_deck = deck_list[idx]
    else:
        for d in deck_list:
            if str(d.get('id')) == sel:
                chosen_deck = d
                break

    if not chosen_deck:
        print('选择无效，已取消。')
        sys.exit(0)

    deck_id = chosen_deck.get('id')

    # 获取总部列表（优先 Data/locations 目录）
    locations_list = []
    try:
        import os
        loc_dir = os.path.join('Data', 'locations')
        if os.path.isdir(loc_dir):
            for fname in sorted(os.listdir(loc_dir)):
                if not fname or fname.startswith('.'):
                    continue
                key = os.path.splitext(fname)[0]
                locations_list.append({'id': key, 'name': key})
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        try:
            with open('locations.json', 'r', encoding='utf-8') as f:
                loc_raw = json.load(f)
                items = loc_raw.get('locations') or []
                for it in items:
                    _id = it.get('id')
                    _name = it.get('name') or _id
                    if _id:
                        locations_list.append({'id': _id, 'name': _name})
        except FileNotFoundError:
            pass

    if not locations_list:
        print('未能找到可用的总部列表（Data/locations 或 locations.json 均缺失）。')
        sys.exit(1)

    print('可选总部：')
    for i, loc in enumerate(locations_list, start=1):
        print(f"{i}. id={loc['id']} 名称={loc['name']}")

    sel_loc = input('请输入总部编号或 id：').strip()
    chosen_loc = None
    if sel_loc.isdigit():
        idx = int(sel_loc) - 1
        if 0 <= idx < len(locations_list):
            chosen_loc = locations_list[idx]
    else:
        for loc in locations_list:
            if loc['id'] == sel_loc:
                chosen_loc = loc
                break

    if not chosen_loc:
        print('选择无效，已取消。')
        sys.exit(0)

    loc_id = chosen_loc['id']
    print(f'正在将卡组 {deck_id} 的总部更换为 {loc_id} ({chosen_loc["name"]}) ...')

    # 修改选中卡组的 deck_code：将最后一个 '|' 之后的子串的前两位替换为 loc_id
    orig_deck_code = chosen_deck.get('deck_code')
    if not orig_deck_code or '|' not in orig_deck_code:
        print('无法获取原始 deck_code，取消。')
        sys.exit(1)
    last_pipe = orig_deck_code.rfind('|')
    tail = orig_deck_code[last_pipe+1:]
    # 确保 tail 足够长以替换前两位；否则用 loc_id + rest
    if len(tail) >= 2:
        new_tail = loc_id + tail[2:]
    else:
        new_tail = (loc_id + tail)[0:len(tail)]
    new_deck_code = orig_deck_code[:last_pipe+1] + new_tail

    put_resp = safe_put(f'https://kards.live.1939api.com/players/{pid}/decks/{deck_id}', headers=headers_auth, json={
        'action': 'fill',
        'deck_code': new_deck_code,
    })
    if not put_resp or not getattr(put_resp, 'ok', False):
        print(f'更换总部失败: {getattr(put_resp, "status_code", "?")} {getattr(put_resp, "text", "")}')
    else:
        print('总部更换成功。')
elif choice == "7":
    # 一键完成成就：读取 Achievements.json 中的 Rows，构建 setmany 列表
    try:
        with open('Achievements.json', 'r', encoding='utf-8') as f:
            ach_raw = json.load(f)
    except FileNotFoundError:
        print('Achievements.json 未找到，无法完成成就。')
        sys.exit(1)

    # 支持 DataTable 格式：顶层是列表并含 Rows
    rows = {}
    if isinstance(ach_raw, list) and len(ach_raw) > 0 and 'Rows' in ach_raw[0]:
        rows = ach_raw[0].get('Rows', {})
    elif isinstance(ach_raw, dict) and 'Rows' in ach_raw:
        rows = ach_raw.get('Rows', {})
    else:
        # 尝试容错：如果是 dict 的话直接当作 rows
        if isinstance(ach_raw, dict):
            rows = ach_raw

    if not rows:
        print('未能解析 Achievements.json 中的 Rows。')
        sys.exit(1)

    items = []
    for key, val in rows.items():
        # 名称在 title.LocalizedString 或 Text.LocalizedString
        name = None
        if isinstance(val, dict):
            title = val.get('title') or {}
            name = title.get('LocalizedString') or title.get('SourceString')
            counter = val.get('counter') or val.get('Counter') or 1
        else:
            counter = 1
        items.append({'key': key, 'name': name or key, 'counter': counter})

    if not items:
        print('未找到任何成就定义。')
        sys.exit(1)

    print('可完成的成就：')
    for i, it in enumerate(items, start=1):
        print(f"{i}. key={it['key']} 名称={it['name']} 目标={it['counter']}")

    sel = input('输入 all (全部) 或 成就编号 或 key（逗号分隔）: ').strip()
    to_set = []
    if sel.lower() == 'all':
        for it in items:
            to_set.append({'key': it['key'], 'value': it['counter']})
    else:
        parts = [s.strip() for s in sel.split(',') if s.strip()]
        for p in parts:
            if p.isdigit():
                idx = int(p) - 1
                if 0 <= idx < len(items):
                    it = items[idx]
                    to_set.append({'key': it['key'], 'value': it['counter']})
            else:
                for it in items:
                    if it['key'] == p:
                        to_set.append({'key': it['key'], 'value': it['counter']})

    if not to_set:
        print('没有选择任何成就，已取消。')
        sys.exit(0)

    payload = {'action': 'setmany', 'setmany': to_set}
    print(f'准备发送 {len(to_set)} 个成就完成请求...')
    resp = safe_put(f'https://kards.live.1939api.com/players/{pid}/achievements', headers=headers_auth, json=payload)
    if not resp or not getattr(resp, 'ok', False):
        print(f'完成成就失败: {getattr(resp, "status_code", "?")} {getattr(resp, "text", "")}')
    else:
        print('成就完成请求已发送。')
