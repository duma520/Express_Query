# test_kuaidi100_apis.py - 测试快递100多个API接口（增强版）

import hashlib
import json
import requests
from datetime import datetime

# 测试配置
TRACKING_NUM = "76919763332469"  # 中通快递单号
# TRACKING_NUM = "435092520545809"  # 中通快递单号

COMPANY_CODE = "zhongtong"
CUSTOMER = "5010D9611F0729A03E038939171B905B"
AUTH_KEY = "ZWRgIval9273"

# 快递100的多个API端点
API_ENDPOINTS = [
    {
        "name": "标准查询接口 (poll.kuaidi100.com)",
        "url": "https://poll.kuaidi100.com/poll/query.do",
        "method": "POST",
        "params_template": {"customer": CUSTOMER, "sign": "", "param": ""}
    },
    {
        "name": "企业版查询接口 (api.kuaidi100.com)",
        "url": "https://api.kuaidi100.com/enterprise/query",
        "method": "POST",
        "params_template": {"customer": CUSTOMER, "sign": "", "param": ""}
    },
    {
        "name": "实时查询接口 V2 (poll.kuaidi100.com/v2)",
        "url": "https://poll.kuaidi100.com/poll/v2/query.do",
        "method": "POST",
        "params_template": {"customer": CUSTOMER, "sign": "", "param": ""}
    },
    {
        "name": "国际版查询接口 (api.kuaidi100.com/intl)",
        "url": "https://api.kuaidi100.com/intl/query",
        "method": "POST",
        "params_template": {"customer": CUSTOMER, "sign": "", "param": ""}
    },
    {
        "name": "备用查询接口 (m.kuaidi100.com)",
        "url": "https://m.kuaidi100.com/query",
        "method": "GET",
        "params_template": {"type": COMPANY_CODE, "postid": TRACKING_NUM}
    },
    {
        "name": "自动识别接口 (www.kuaidi100.com/autonumber)",
        "url": "https://www.kuaidi100.com/autonumber/auto",
        "method": "POST",
        "params_template": {"num": TRACKING_NUM, "key": AUTH_KEY}
    },
]

def generate_sign(param_str: str) -> str:
    """生成快递100签名"""
    sign_str = param_str + AUTH_KEY + CUSTOMER
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def test_endpoint(endpoint: dict) -> dict:
    """测试单个API端点"""
    result = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "success": False,
        "status_code": None,
        "response": None,
        "error": None,
        "has_data": False,
        "state": None,
        "message": None,
        "data": []
    }
    
    try:
        # 准备参数
        if "param" in endpoint["params_template"]:
            param_data = {
                "com": COMPANY_CODE,
                "num": TRACKING_NUM,
                "phone": "",  # 可选
                "from": "",
                "to": "",
                "resultv2": "1"  # 使用v2版本结果
            }
            param_str = json.dumps(param_data, separators=(',', ':'))
            sign = generate_sign(param_str)
            
            data = {
                "customer": CUSTOMER,
                "sign": sign,
                "param": param_str
            }
        else:
            # 使用模板参数
            data = endpoint["params_template"].copy()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 发送请求
        if endpoint["method"] == "POST":
            response = requests.post(
                endpoint["url"], 
                data=data, 
                headers=headers, 
                timeout=15
            )
        else:
            response = requests.get(
                endpoint["url"], 
                params=data, 
                headers=headers, 
                timeout=15
            )
        
        result["status_code"] = response.status_code
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                result["response"] = resp_json
                result["state"] = resp_json.get("state")
                result["message"] = resp_json.get("message")
                result["status"] = resp_json.get("status")
                result["data"] = resp_json.get("data", [])
                
                # 判断是否成功
                if resp_json.get("status") == "200" or resp_json.get("returnCode") == "200":
                    result["success"] = True
                    result["has_data"] = len(resp_json.get("data", [])) > 0
                elif resp_json.get("message") == "ok" and resp_json.get("data"):
                    result["success"] = True
                    result["has_data"] = True
                elif resp_json.get("nu") == TRACKING_NUM:
                    result["success"] = True
                    result["has_data"] = len(resp_json.get("data", [])) > 0
                    
            except json.JSONDecodeError:
                result["error"] = "JSON解析失败"
                result["response"] = response.text[:200]
        else:
            result["error"] = f"HTTP {response.status_code}"
            result["response"] = response.text[:200]
            
    except requests.exceptions.Timeout:
        result["error"] = "请求超时"
    except requests.exceptions.ConnectionError:
        result["error"] = "连接失败"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def print_separator(char="=", length=80):
    print(char * length)

def print_result(result: dict, show_full_track: bool = False):
    """打印单个测试结果"""
    print_separator("-")
    
    # 状态标识
    if result["success"]:
        status_icon = "✅"
        status_text = "成功"
    else:
        status_icon = "❌"
        status_text = "失败"
    
    print(f"{status_icon} {result['name']}")
    print(f"   URL: {result['url']}")
    print(f"   状态: {status_text}")
    
    if result["status_code"]:
        print(f"   HTTP状态码: {result['status_code']}")
    
    if result["state"]:
        state_text = {
            "0": "在途中",
            "1": "已揽收",
            "2": "疑难",
            "3": "已签收",
            "4": "退签",
            "5": "派件中",
            "6": "退回",
            "7": "转单",
            "8": "待清关",
            "9": "清关中",
            "10": "已清关",
            "14": "到件"
        }.get(str(result["state"]), f"状态码{result['state']}")
        print(f"   物流状态: {state_text} (state={result['state']})")
    
    if result["message"]:
        print(f"   消息: {result['message']}")
    
    if result["has_data"]:
        data = result.get("data", [])
        data_count = len(data)
        print(f"   📦 物流轨迹: {data_count} 条")
        
        if show_full_track and data_count > 0:
            print_separator(".")
            print("   【完整物流轨迹】")
            print_separator(".")
            for i, track in enumerate(data, 1):
                time = track.get('time', '未知时间')
                context = track.get('context', '未知')
                location = track.get('location', '')
                ftime = track.get('ftime', '')
                
                print(f"   {i}. [{time}]")
                print(f"      {context}")
                if location:
                    print(f"      地点: {location}")
                if ftime:
                    print(f"      时间戳: {ftime}")
                print()
        else:
            # 显示最新的3条轨迹
            if data_count > 0:
                print("   最新轨迹:")
                for i, track in enumerate(data[:3]):
                    print(f"     {i+1}. [{track.get('time', '未知')}] {track.get('context', '未知')[:60]}...")
                if data_count > 3:
                    print(f"     ... 还有 {data_count - 3} 条轨迹")
    
    if result["error"]:
        print(f"   ⚠️ 错误: {result['error']}")
    
    if result["response"] and not result["success"]:
        print(f"   响应预览: {str(result['response'])[:150]}")

def print_detailed_track(data: list):
    """打印详细的物流轨迹分析"""
    if not data:
        return
    
    print_separator("=")
    print("📋 详细轨迹分析")
    print_separator("=")
    
    # 按时间倒序排列（最新的在前）
    sorted_data = sorted(data, key=lambda x: x.get('time', ''), reverse=True)
    
    # 统计信息
    total_tracks = len(sorted_data)
    first_time = sorted_data[-1].get('time', '') if sorted_data else ''
    last_time = sorted_data[0].get('time', '') if sorted_data else ''
    
    print(f"总轨迹数: {total_tracks}")
    print(f"时间跨度: {first_time} → {last_time}")
    
    # 关键节点
    print_separator("-")
    print("关键节点:")
    key_nodes = []
    for track in data:
        context = track.get('context', '')
        time = track.get('time', '')
        if any(kw in context for kw in ['揽收', '收件', '取件']):
            key_nodes.append(('📮 揽收', time, context))
        elif any(kw in context for kw in ['签收', '已收']):
            key_nodes.append(('✅ 签收', time, context))
        elif any(kw in context for kw in ['派送', '派件']):
            key_nodes.append(('🚚 派送中', time, context))
        elif any(kw in context for kw in ['到达', '抵达']):
            if '转运中心' in context or '分拨' in context:
                key_nodes.append(('📍 到达转运中心', time, context))
            else:
                key_nodes.append(('📍 到达', time, context))
        elif any(kw in context for kw in ['离开', '发往']):
            key_nodes.append(('✈️ 离开/发往', time, context))
    
    for icon, time, context in key_nodes[:10]:  # 最多显示10个
        print(f"  {icon} [{time}] {context[:50]}...")
    
    print_separator("=")

def main():
    print_separator()
    print(f"快递100 API 接口测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试单号: {TRACKING_NUM}")
    print(f"快递公司: {COMPANY_CODE}")
    print(f"测试说明: 中通快递单号，查找可用的API接口")
    print_separator()
    
    results = []
    success_count = 0
    success_result = None
    
    for i, endpoint in enumerate(API_ENDPOINTS, 1):
        print(f"\n[{i}/{len(API_ENDPOINTS)}] 正在测试: {endpoint['name']}")
        result = test_endpoint(endpoint)
        results.append(result)
        
        if result["success"]:
            print_result(result, show_full_track=False)  # 先简要显示
            success_count += 1
            success_result = result
        else:
            print_result(result)
    
    # 总结
    print_separator()
    print(f"测试完成！")
    print(f"总接口数: {len(API_ENDPOINTS)}")
    print(f"成功接口: {success_count}")
    print(f"失败接口: {len(API_ENDPOINTS) - success_count}")
    
    # 显示成功的接口详情
    if success_count > 0:
        print_separator("=")
        print("✅ 成功的接口及完整轨迹:")
        print_separator("=")
        for result in results:
            if result["success"]:
                print(f"\n接口: {result['name']}")
                print(f"URL: {result['url']}")
                print_detailed_track(result.get("data", []))
                
                # 打印完整轨迹列表
                print_separator("-")
                print("完整轨迹列表:")
                print_separator("-")
                data = result.get("data", [])
                if data:
                    # 按时间正序显示（从旧到新）
                    sorted_data = sorted(data, key=lambda x: x.get('time', ''))
                    for i, track in enumerate(sorted_data, 1):
                        time = track.get('time', '未知时间')
                        context = track.get('context', '未知')
                        location = track.get('location', '')
                        
                        print(f"{i:2d}. [{time}]")
                        print(f"    {context}")
                        if location:
                            print(f"    地点: {location}")
                        print()
                else:
                    print("   （无轨迹数据）")
    
    # 保存详细结果到文件
    output_file = f"api_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 清理response字段以便保存（避免循环引用）
    save_results = []
    for r in results:
        save_r = r.copy()
        if "response" in save_r:
            # response已经保存了完整数据，可以保留
            pass
        save_results.append(save_r)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n详细结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    results = main()