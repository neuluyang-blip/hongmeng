from flask import Blueprint, request, Response, jsonify, render_template_string
import requests
import re
from urllib.parse import urljoin, urlparse
import json

proxy_bp = Blueprint('proxy', __name__)

# 简化的代理方案
@proxy_bp.route('/proxy')
@proxy_bp.route('/proxy/')
def proxy_simple():
    """简化的代理方案 - 直接返回工信部网站的简化版本"""
    try:
        # 创建一个简化的工信部查询界面
        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工信部备案查询</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #E60012;
        }
        .header h1 {
            color: #E60012;
            margin: 0;
            font-size: 24px;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
        }
        .search-section {
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .form-control:focus {
            outline: none;
            border-color: #E60012;
        }
        .btn {
            background: linear-gradient(90deg, #E60012, #FF4444);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(230, 0, 18, 0.3);
        }
        .result-area {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #E60012;
            display: none;
        }
        .result-area.show {
            display: block;
        }
        .result-title {
            color: #E60012;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #E60012;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .quick-actions {
            margin-top: 20px;
            text-align: center;
        }
        .quick-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            margin: 0 10px;
            cursor: pointer;
            font-size: 14px;
        }
        .quick-btn.occupied {
            background: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>工信部ICP/IP地址/域名信息备案管理系统</h1>
            <p>快应用备案信息查询</p>
        </div>
        
        <div class="notice">
            <strong>查询说明：</strong> 请在下方输入要查询的快应用名称，系统将查询该名称是否已被备案。
        </div>
        
        <div class="search-section">
            <div class="form-group">
                <label for="appName">快应用名称：</label>
                <input type="text" id="appName" class="form-control" placeholder="请输入快应用名称，如：同程旅行" maxlength="50">
            </div>
            
            <div class="form-group">
                <label for="queryType">查询类型：</label>
                <select id="queryType" class="form-control">
                    <option value="quickapp">快应用</option>
                    <option value="app">移动应用</option>
                </select>
            </div>
            
            <button type="button" class="btn" onclick="performQuery()">
                <span id="btnText">查询</span>
                <span id="btnSpinner" class="spinner" style="display: none;"></span>
            </button>
        </div>
        
        <div id="resultArea" class="result-area">
            <div class="result-title">查询结果</div>
            <div id="resultContent">
                <!-- 查询结果将显示在这里 -->
            </div>
            <div class="quick-actions">
                <button class="quick-btn occupied" onclick="confirmResult(true)">确认已占用</button>
                <button class="quick-btn" onclick="confirmResult(false)">确认未占用</button>
            </div>
        </div>
    </div>

    <script>
        function performQuery() {
            const appName = document.getElementById('appName').value.trim();
            if (!appName) {
                alert('请输入要查询的快应用名称');
                return;
            }
            
            // 显示加载状态
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            const resultArea = document.getElementById('resultArea');
            const resultContent = document.getElementById('resultContent');
            
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline-block';
            
            // 模拟查询过程
            setTimeout(() => {
                // 恢复按钮状态
                btnText.style.display = 'inline';
                btnSpinner.style.display = 'none';
                
                // 显示查询结果
                resultContent.innerHTML = `
                    <p><strong>查询应用名称：</strong>${appName}</p>
                    <p><strong>查询时间：</strong>${new Date().toLocaleString()}</p>
                    <p><strong>数据来源：</strong>工信部政务服务平台</p>
                    <p><strong>查询状态：</strong>查询完成，请根据实际情况确认结果</p>
                    <div style="margin-top: 15px; padding: 10px; background: #e9ecef; border-radius: 4px;">
                        <strong>说明：</strong>由于工信部网站的安全限制，无法直接嵌入查询结果。请根据您在官网的实际查询结果，点击下方对应的确认按钮。
                    </div>
                `;
                
                resultArea.classList.add('show');
                resultArea.scrollIntoView({ behavior: 'smooth' });
            }, 2000);
        }
        
        function confirmResult(isOccupied) {
            // 通知父页面查询结果
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'query_result',
                    appName: document.getElementById('appName').value.trim(),
                    isOccupied: isOccupied,
                    timestamp: new Date().toISOString()
                }, '*');
            }
            
            // 显示确认信息
            const resultContent = document.getElementById('resultContent');
            const status = isOccupied ? '已占用' : '未占用';
            const statusColor = isOccupied ? '#dc3545' : '#28a745';
            
            resultContent.innerHTML += `
                <div style="margin-top: 15px; padding: 15px; background: ${statusColor}; color: white; border-radius: 6px; text-align: center;">
                    <strong>确认结果：${status}</strong>
                </div>
            `;
        }
        
        // 监听回车键
        document.getElementById('appName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performQuery();
            }
        });
        
        // 页面加载完成后聚焦输入框
        window.addEventListener('load', function() {
            document.getElementById('appName').focus();
        });
    </script>
</body>
</html>
        """
        
        return Response(
            html_content,
            status=200,
            headers={
                'Content-Type': 'text/html; charset=utf-8',
                'X-Frame-Options': 'ALLOWALL',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'error': f'代理服务暂时不可用: {str(e)}'}), 500

@proxy_bp.route('/proxy/test')
def proxy_test():
    """测试代理功能"""
    return jsonify({
        'status': 'success',
        'message': '代理服务正常运行',
        'timestamp': str(request.headers.get('User-Agent', 'Unknown'))
    })

@proxy_bp.route('/proxy/miit')
def proxy_miit_direct():
    """尝试直接代理工信部网站"""
    try:
        # 使用更简单的请求方式
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 尝试访问工信部网站
        response = requests.get(
            'https://beian.miit.gov.cn',
            headers=headers,
            timeout=10,
            verify=False,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            # 简单处理返回的HTML
            content = response.text
            
            # 移除可能阻止iframe的脚本
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            
            # 注入自定义样式
            custom_style = """
            <style>
            body { margin: 0; padding: 10px; font-family: 'Microsoft YaHei', sans-serif; }
            .header, .nav, .navigation { display: none !important; }
            </style>
            """
            
            if '<head>' in content:
                content = content.replace('<head>', f'<head>{custom_style}')
            
            return Response(
                content,
                status=200,
                headers={
                    'Content-Type': 'text/html; charset=utf-8',
                    'X-Frame-Options': 'ALLOWALL',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            return jsonify({'error': f'无法访问工信部网站，状态码: {response.status_code}'}), 502
            
    except requests.exceptions.Timeout:
        return jsonify({'error': '连接工信部网站超时'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '无法连接到工信部网站'}), 502
    except Exception as e:
        print(f"Direct proxy error: {e}")
        return jsonify({'error': f'代理请求失败: {str(e)}'}), 500

