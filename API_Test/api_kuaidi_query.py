import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import hashlib
import time
from datetime import datetime
import re

class ExpressQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("快递查询系统 v2.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 快递公司代码映射
        self.company_codes = {
            "自动识别": "",
            "顺丰速运": "shunfeng",
            "圆通速递": "yuantong",
            "中通快递": "zhongtong",
            "韵达快递": "yunda",
            "申通快递": "shentong",
            "百世快递": "huitongkuaidi",
            "京东物流": "jd",
            "中国邮政": "youzhengguo",
            "EMS": "ems",
            "天天快递": "tiantian",
            "德邦快递": "debangwuliu",
            "极兔速递": "jtexpress",
            "宅急送": "zhaijisong"
        }
        
        # 使用快递100的免费公开接口（不需要API key）
        self.apis = {
            "快递100公开接口": "https://www.kuaidi100.com/query",
            "快递鸟测试接口": "https://sandbox.kdniao.com/External/QueryOrder",
            "备用查询接口 (m.kuaidi100.com)": "https://m.kuaidi100.com/query",
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="快递查询系统", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # API选择
        ttk.Label(main_frame, text="选择API:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.api_var = tk.StringVar()
        self.api_combo = ttk.Combobox(main_frame, textvariable=self.api_var, 
                                     values=list(self.apis.keys()), 
                                     state="readonly", width=25)
        self.api_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.api_combo.set("快递100公开接口")
        
        # 查询模式选择
        ttk.Label(main_frame, text="查询模式:", font=("Arial", 10)).grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        self.mode_var = tk.StringVar(value="auto")
        auto_radio = ttk.Radiobutton(main_frame, text="自动识别", variable=self.mode_var, 
                                     value="auto", command=self.on_mode_change)
        auto_radio.grid(row=1, column=3, sticky=tk.W, pady=5)
        manual_radio = ttk.Radiobutton(main_frame, text="手动选择", variable=self.mode_var, 
                                       value="manual", command=self.on_mode_change)
        manual_radio.grid(row=1, column=4, sticky=tk.W, pady=5, padx=5)
        
        # 快递单号输入
        ttk.Label(main_frame, text="快递单号:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.tracking_num = ttk.Entry(main_frame, width=50, font=("Arial", 10))
        self.tracking_num.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # 快递公司选择（手动模式）
        ttk.Label(main_frame, text="快递公司:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(main_frame, textvariable=self.company_var, 
                                         values=list(self.company_codes.keys()), 
                                         state="readonly", width=30)
        self.company_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        self.company_combo.set("圆通速递")
        self.company_combo.config(state="disabled")
        
        # 查询按钮
        self.query_btn = ttk.Button(main_frame, text="查询物流", command=self.query_express, 
                                    style="Accent.TButton")
        self.query_btn.grid(row=4, column=0, columnspan=4, pady=15)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=5, column=0, columnspan=4, pady=5)
        
        # 结果显示区域
        ttk.Label(main_frame, text="物流轨迹:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(main_frame, width=100, height=25, font=("Arial", 9))
        self.result_text.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # 设置样式
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
        # 配置文本标签样式
        self.result_text.tag_config("title", font=("Arial", 12, "bold"), foreground="blue")
        self.result_text.tag_config("info", font=("Arial", 10), foreground="green")
        self.result_text.tag_config("error", font=("Arial", 10), foreground="red")
        self.result_text.tag_config("warning", font=("Arial", 10), foreground="orange")
        self.result_text.tag_config("normal", font=("Arial", 10), foreground="black")
        self.result_text.tag_config("track", font=("Arial", 9), foreground="#333333")
        
    def on_mode_change(self):
        """查询模式切换"""
        if self.mode_var.get() == "auto":
            self.company_combo.config(state="disabled")
        else:
            self.company_combo.config(state="readonly")
    
    def auto_recognize_company(self, tracking_num):
        """自动识别快递公司 - 使用快递100的自动识别接口"""
        try:
            url = "https://www.kuaidi100.com/autonumber/auto"
            params = {"num": tracking_num}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    company_info = data[0]
                    company_name = company_info.get("name", "")
                    company_code = company_info.get("code", "")
                    
                    self.result_text.insert(tk.END, f"🤖 自动识别结果: {company_name}\n", "info")
                    return company_code, company_name
            return None, None
        except Exception as e:
            self.result_text.insert(tk.END, f"⚠️ 自动识别失败: {str(e)}\n", "error")
            return None, None
    
    def detect_company_by_number(self, tracking_num):
        """根据单号格式自动识别快递公司（备用方案）"""
        tracking_num = tracking_num.strip().upper()
        
        # 快递单号识别规则
        rules = [
            # 圆通速递 YT开头
            (lambda n: n.startswith('YT') and len(n) >= 10, 'yuantong', '圆通速递'),
            # 中通快递 ZT开头或7/8开头
            (lambda n: n.startswith('ZT') and len(n) >= 10, 'zhongtong', '中通快递'),
            (lambda n: len(n) >= 10 and n.isdigit() and n[0] in '78', 'zhongtong', '中通快递'),
            # 韵达快递 YD开头或1/4/5开头
            (lambda n: n.startswith('YD') and len(n) >= 10, 'yunda', '韵达快递'),
            (lambda n: len(n) == 13 and n.isdigit() and n[0] in '145', 'yunda', '韵达快递'),
            # 申通快递 ST开头或3/7/8开头
            (lambda n: n.startswith('ST') and len(n) >= 10, 'shentong', '申通快递'),
            (lambda n: len(n) == 12 and n.isdigit() and n[0] in '378', 'shentong', '申通快递'),
            # 顺丰速运 SF开头
            (lambda n: n.startswith('SF') and len(n) >= 12, 'shunfeng', '顺丰速运'),
            # 京东物流 JD开头
            (lambda n: n.startswith('JD'), 'jd', '京东物流'),
            # 极兔速递 JT开头
            (lambda n: n.startswith('JT') and len(n) >= 10, 'jtexpress', '极兔速递'),
            # EMS EMS开头或98/99开头
            (lambda n: n.startswith('EMS'), 'ems', 'EMS'),
            (lambda n: len(n) == 13 and n.isdigit() and n[:2] in ['98', '99', '10', '11'], 'ems', 'EMS'),
            # 德邦快递 DPK开头
            (lambda n: n.startswith('DPK') and len(n) >= 10, 'debangwuliu', '德邦快递'),
        ]
        
        for check, code, name in rules:
            try:
                if check(tracking_num):
                    return code, name
            except:
                continue
                
        return None, None
    
    def query_kuaidi100_api(self, tracking_num, company_code):
        """使用快递100公开接口查询（不需要API key）"""
        try:
            url = "https://www.kuaidi100.com/query"
            params = {
                "type": company_code,
                "postid": tracking_num,
                "temp": int(time.time())
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.kuaidi100.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查返回状态
                if result.get("status") == "200":
                    self.display_tracking_info(result)
                    return True
                elif result.get("message") == "ok":
                    self.display_tracking_info(result)
                    return True
                else:
                    error_msg = result.get('message', '查询失败')
                    self.result_text.insert(tk.END, f"❌ 查询失败: {error_msg}\n", "error")
                    return False
            else:
                self.result_text.insert(tk.END, f"❌ HTTP错误: {response.status_code}\n", "error")
                return False
                
        except Exception as e:
            self.result_text.insert(tk.END, f"❌ 异常: {str(e)}\n", "error")
            return False
    
    def query_kuaidiy_api(self, tracking_num, company_code):
        """使用快递网接口查询"""
        try:
            url = "https://www.kuaidiy.com/index/index/query.html"
            params = {
                "com": company_code,
                "nu": tracking_num
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.kuaidiy.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == 1:
                    # 转换数据格式
                    formatted_result = {
                        "nu": tracking_num,
                        "com": company_code,
                        "state": result.get("state", "0"),
                        "data": result.get("data", [])
                    }
                    self.display_tracking_info(formatted_result)
                    return True
                else:
                    error_msg = result.get('msg', '查询失败')
                    self.result_text.insert(tk.END, f"❌ 查询失败: {error_msg}\n", "error")
                    return False
            else:
                self.result_text.insert(tk.END, f"❌ HTTP错误: {response.status_code}\n", "error")
                return False
                
        except Exception as e:
            self.result_text.insert(tk.END, f"❌ 异常: {str(e)}\n", "error")
            return False
    
    def query_ickd_api(self, tracking_num, company_code):
        """使用爱查快递接口查询"""
        try:
            url = "https://www.ickd.cn/query"
            params = {
                "com": company_code,
                "nu": tracking_num
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.ickd.cn/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # 该接口返回HTML，需要解析
                html_content = response.text
                
                # 尝试从HTML中提取物流信息
                pattern = r'<div class="track-item">.*?<div class="time">(.*?)</div>.*?<div class="content">(.*?)</div>'
                matches = re.findall(pattern, html_content, re.DOTALL)
                
                if matches:
                    data_list = []
                    for match in matches:
                        data_list.append({
                            "time": match[0].strip(),
                            "context": match[1].strip()
                        })
                    
                    result = {
                        "nu": tracking_num,
                        "com": company_code,
                        "state": "0",
                        "data": data_list
                    }
                    self.display_tracking_info(result)
                    return True
                else:
                    self.result_text.insert(tk.END, "❌ 无法解析物流信息\n", "error")
                    return False
            else:
                self.result_text.insert(tk.END, f"❌ HTTP错误: {response.status_code}\n", "error")
                return False
                
        except Exception as e:
            self.result_text.insert(tk.END, f"❌ 异常: {str(e)}\n", "error")
            return False
    
    def display_tracking_info(self, data):
        """显示物流轨迹信息"""
        self.result_text.delete(1.0, tk.END)
        
        # 显示基本信息
        self.result_text.insert(tk.END, "📦 快递物流信息\n", "title")
        self.result_text.insert(tk.END, f"{'='*70}\n", "normal")
        
        # 显示快递状态
        state_map = {
            "0": "📋 在途中", 
            "1": "📮 已揽收", 
            "2": "⚠️ 疑难", 
            "3": "✅ 已签收", 
            "4": "↩️ 退签",
            "5": "🚚 派件中",
            "6": "↩️ 退回",
            "7": "🔄 转单"
        }
        state = data.get("state", "")
        state_text = state_map.get(str(state), f"状态码{state}")
        
        self.result_text.insert(tk.END, f"快递单号: {data.get('nu', '')}\n", "info")
        
        # 获取公司名称
        com_code = data.get('com', '')
        com_name = com_code
        for name, code in self.company_codes.items():
            if code == com_code:
                com_name = name
                break
        self.result_text.insert(tk.END, f"快递公司: {com_name}\n", "info")
        self.result_text.insert(tk.END, f"当前状态: {state_text}\n", "info")
        
        # 显示物流轨迹统计
        data_list = data.get("data", [])
        if data_list:
            self.result_text.insert(tk.END, f"轨迹数量: {len(data_list)} 条\n", "info")
            
            # 计算时间跨度
            times = [item.get('time', '') for item in data_list if item.get('time')]
            if len(times) >= 2:
                self.result_text.insert(tk.END, f"时间跨度: {times[-1]} → {times[0]}\n", "info")
        
        self.result_text.insert(tk.END, f"{'='*70}\n\n", "normal")
        
        # 显示物流轨迹
        self.result_text.insert(tk.END, "📍 物流轨迹（从旧到新）:\n", "title")
        self.result_text.insert(tk.END, f"{'-'*70}\n", "normal")
        
        if data_list:
            # 按时间正序显示（从旧到新）
            sorted_data = sorted(data_list, key=lambda x: x.get('time', ''))
            
            for i, item in enumerate(sorted_data, 1):
                time_str = item.get("time", "未知时间")
                context = item.get("context", "未知")
                
                # 根据状态设置图标
                icon = "📍"
                if "签收" in context or "已收" in context:
                    icon = "✅"
                elif "派送" in context or "派件" in context:
                    icon = "🚚"
                elif "揽收" in context or "收件" in context:
                    icon = "📮"
                elif "到达" in context or "抵达" in context:
                    icon = "🏢"
                elif "离开" in context or "发往" in context:
                    icon = "✈️"
                
                self.result_text.insert(tk.END, f"{i:2d}. {icon} [{time_str}]\n", "track")
                self.result_text.insert(tk.END, f"     {context}\n", "track")
                self.result_text.insert(tk.END, f"     {'-'*60}\n", "track")
        else:
            self.result_text.insert(tk.END, "暂无物流轨迹信息\n", "warning")
            self.result_text.insert(tk.END, "\n💡 温馨提示:\n", "info")
            self.result_text.insert(tk.END, "  1. 快递单号可能还未录入系统\n", "info")
            self.result_text.insert(tk.END, "  2. 请稍后再试\n", "info")
            self.result_text.insert(tk.END, "  3. 也可以尝试切换其他API接口\n", "info")
    
    def query_express(self):
        """执行快递查询"""
        tracking_num = self.tracking_num.get().strip()
        
        if not tracking_num:
            messagebox.showwarning("提示", "请输入快递单号")
            return
        
        # 清空结果显示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🔍 正在查询中，请稍候...\n", "info")
        
        # 启动进度条
        self.progress.start(10)
        self.query_btn.config(state="disabled")
        self.root.update()
        
        try:
            # 获取快递公司代码
            company_code = None
            company_name = None
            
            if self.mode_var.get() == "auto":
                # 自动识别
                company_code, company_name = self.auto_recognize_company(tracking_num)
                if not company_code:
                    # 自动识别失败，使用本地格式识别
                    company_code, company_name = self.detect_company_by_number(tracking_num)
                    if company_code:
                        self.result_text.insert(tk.END, f"🤖 格式识别结果: {company_name}\n", "info")
                    else:
                        # 如果都无法识别，默认使用圆通
                        company_code = "yuantong"
                        company_name = "圆通速递"
                        self.result_text.insert(tk.END, f"⚠️ 无法识别快递公司，默认使用: {company_name}\n", "warning")
            else:
                # 手动选择
                company_name = self.company_var.get()
                if company_name in self.company_codes:
                    company_code = self.company_codes[company_name]
                else:
                    messagebox.showerror("错误", "请选择有效的快递公司")
                    return
            
            self.result_text.insert(tk.END, f"📋 快递公司: {company_name} ({company_code})\n", "info")
            self.result_text.insert(tk.END, f"{'='*70}\n\n", "normal")
            
            # 根据选择的API进行查询
            api_name = self.api_var.get()
            success = False
            
            if api_name == "快递100公开接口":
                success = self.query_kuaidi100_api(tracking_num, company_code)
            elif api_name == "快递网接口":
                success = self.query_kuaidiy_api(tracking_num, company_code)
            elif api_name == "爱查快递接口":
                success = self.query_ickd_api(tracking_num, company_code)
            else:
                success = self.query_kuaidi100_api(tracking_num, company_code)
            
            if not success:
                self.result_text.insert(tk.END, "\n💡 提示: 如果查询失败，可以尝试:\n", "warning")
                self.result_text.insert(tk.END, "  1. 切换其他API接口\n", "warning")
                self.result_text.insert(tk.END, "  2. 检查快递单号是否正确\n", "warning")
                self.result_text.insert(tk.END, "  3. 确认快递公司是否正确\n", "warning")
                self.result_text.insert(tk.END, "  4. 快递可能还未揽件，请稍后再试\n", "warning")
                
        except Exception as e:
            messagebox.showerror("错误", f"查询过程发生异常: {str(e)}")
            self.result_text.insert(tk.END, f"❌ 异常: {str(e)}\n", "error")
        finally:
            # 停止进度条
            self.progress.stop()
            self.query_btn.config(state="normal")

def main():
    root = tk.Tk()
    app = ExpressQueryApp(root)
    
    # 显示使用说明
    messagebox.showinfo("使用说明", 
                       "📦 快递查询系统 v2.1\n\n"
                       "功能特点:\n"
                       "✓ 使用快递100公开接口（无需API Key）\n"
                       "✓ 支持自动识别快递公司\n"
                       "✓ 支持多种API接口\n"
                       "✓ 清晰的物流轨迹显示\n\n"
                       "使用步骤:\n"
                       "1. 选择API接口（推荐快递100公开接口）\n"
                       "2. 选择查询模式（自动识别或手动选择）\n"
                       "3. 输入快递单号\n"
                       "4. 点击查询物流\n\n"
                       "测试单号: YT7614483885885 (圆通)\n"
                       "        76918242478173 (中通)\n\n"
                       "注意: 使用公开接口无需注册，直接可用")
    
    root.mainloop()

if __name__ == "__main__":
    main()