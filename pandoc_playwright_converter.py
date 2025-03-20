import os
import asyncio
import pypandoc
from playwright.async_api import async_playwright

async def convert_markdown_to_pdf():
    # 获取当前目录下"answer"文件夹的路径
    answer_dir = os.path.join(os.getcwd(), 'answer')
    
    # 检查answer目录是否存在
    if not os.path.isdir(answer_dir):
        print(f"错误: 目录 {answer_dir} 不存在。")
        return
    
    # 查找answer目录中所有的.md文件
    md_files = [f for f in os.listdir(answer_dir) if f.endswith('.md')]
    
    if not md_files:
        print(f"在 {answer_dir} 中未找到Markdown文件。")
        return
    
    print(f"找到 {len(md_files)} 个Markdown文件。正在转换为PDF...")
    
    # 使用Playwright启动浏览器
    async with async_playwright() as p:
        # 启动浏览器（可选择 chromium, firefox, webkit）
        browser = await p.chromium.launch()
        
        # 转换每个Markdown文件为PDF
        for md_file in md_files:
            md_path = os.path.join(answer_dir, md_file)
            html_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.html')
            pdf_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.pdf')
            
            try:
                # 读取Markdown内容检查特殊字符
                with open(md_path, encoding='utf-8') as f:
                    text = f.read()

                # 使用pypandoc将Markdown转换为HTML
                html_content = pypandoc.convert_text(
                    text,
                    'html',
                    format='markdown',
                    extra_args=['--standalone']
                )
                
                # 检查转换后的HTML中是否仍存在"✅"
                if "✅" in html_content:
                    print(f"在 {md_file} 的pypandoc转换后仍存在 ✅")
                else:
                    print(f"警告: 在 {md_file} 的pypandoc转换过程中 ✅ 丢失了")
                
                # 添加基本样式，使PDF更美观，并支持中文和表情符号
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Color+Emoji&display=swap');
                        body {{
                            font-family: 'Noto Sans SC', 'Noto Color Emoji', Arial, sans-serif;
                            margin: 40px;
                            line-height: 1.6;
                        }}
                        h1, h2, h3 {{ color: #333; }}
                        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #555; }}
                        img {{ max-width: 100%; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # 保存中间HTML文件
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                    print(f"保存中间HTML文件: {html_path}")
                
                # 检查最终HTML中是否存在"✅"
                if "✅" in styled_html:
                    print(f"{md_file}的HTML文件中存在 ✅")
                else:
                    print(f"警告: {md_file}的HTML文件中未找到 ✅")
                
                # 创建新页面并导航到HTML文件
                page = await browser.new_page()
                await page.goto(f"file://{os.path.abspath(html_path)}")
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 导出为PDF
                await page.pdf(path=pdf_path, format="A4", margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm"
                })
                
                await page.close()
                print(f"成功将 {md_file} 转换为PDF。")
                
            except Exception as e:
                print(f"转换 {md_file} 时出错: {str(e)}")
        
        # 关闭浏览器
        await browser.close()

# 同步版本的转换函数
def convert_markdown_to_pdf_sync():
    from playwright.sync_api import sync_playwright
    
    # 获取当前目录下"answer"文件夹的路径
    answer_dir = os.path.join(os.getcwd(), 'answer')
    
    # 检查answer目录是否存在
    if not os.path.isdir(answer_dir):
        print(f"错误: 目录 {answer_dir} 不存在。")
        return
    
    # 查找answer目录中所有的.md文件
    md_files = [f for f in os.listdir(answer_dir) if f.endswith('.md')]
    
    if not md_files:
        print(f"在 {answer_dir} 中未找到Markdown文件。")
        return
    
    print(f"找到 {len(md_files)} 个Markdown文件。正在转换为PDF...")
    
    # 使用Playwright启动浏览器
    with sync_playwright() as p:
        # 启动浏览器（可选择 chromium, firefox, webkit）
        browser = p.chromium.launch()
        
        # 转换每个Markdown文件为PDF
        for md_file in md_files:
            md_path = os.path.join(answer_dir, md_file)
            html_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.html')
            pdf_path = os.path.join(answer_dir, os.path.splitext(md_file)[0] + '.pdf')
            
            try:
                # 读取Markdown内容检查特殊字符
                with open(md_path, encoding='utf-8') as f:
                    text = f.read()
                    
                # 检查Markdown中是否存在"✅"
                if "✅" in text:
                    print(f"在 {md_file} 中发现 ✅")
                
                # 使用pypandoc将Markdown转换为HTML
                html_content = pypandoc.convert_text(
                    text,
                    'html',
                    format='markdown',
                    extra_args=['--standalone']
                )
                
                # 检查转换后的HTML中是否仍存在"✅"
                if "✅" in html_content:
                    print(f"在 {md_file} 的pypandoc转换后仍存在 ✅")
                else:
                    print(f"警告: 在 {md_file} 的pypandoc转换过程中 ✅ 丢失了")
                
                # 添加基本样式，使PDF更美观，并支持中文和表情符号
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Color+Emoji&display=swap');
                        body {{
                            font-family: 'Noto Sans SC', 'Noto Color Emoji', Arial, sans-serif;
                            margin: 40px;
                            line-height: 1.6;
                        }}
                        h1, h2, h3 {{ color: #333; }}
                        code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                        blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #555; }}
                        img {{ max-width: 100%; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # 保存中间HTML文件
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                    print(f"保存中间HTML文件: {html_path}")
                
                # 检查最终HTML中是否存在"✅"
                if "✅" in styled_html:
                    print(f"{md_file}的HTML文件中存在 ✅")
                else:
                    print(f"警告: {md_file}的HTML文件中未找到 ✅")
                
                # 创建新页面并导航到HTML文件
                page = browser.new_page()
                page.goto(f"file://{os.path.abspath(html_path)}")
                
                # 等待页面加载完成
                page.wait_for_load_state("networkidle")
                
                # 导出为PDF
                page.pdf(path=pdf_path, format="A4", margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm"
                })
                
                page.close()
                print(f"成功将 {md_file} 转换为PDF。")
                
            except Exception as e:
                print(f"转换 {md_file} 时出错: {str(e)}")
        
        # 关闭浏览器
        browser.close()

# 直接将特定Markdown文件转换为HTML
def convert_md_to_html(input_file, output_file=None):
    """
    将Markdown文件转换为HTML文件
    
    参数:
    input_file -- Markdown文件路径
    output_file -- 输出HTML文件路径（可选）
    """
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.html'
    
    try:
        # 读取Markdown内容
        with open(input_file, encoding='utf-8') as f:
            text = f.read()
        
        # 使用pypandoc将Markdown转换为HTML
        html_content = pypandoc.convert_text(
            text,
            'html',
            format='markdown',
            extra_args=['--standalone']
        )
        
        # 添加基本样式
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&family=Noto+Color+Emoji&display=swap');
                body {{
                    font-family: 'Noto Sans SC', 'Noto Color Emoji', Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                h1, h2, h3 {{ color: #333; }}
                code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #555; }}
                img {{ max-width: 100%; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # 保存HTML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        print(f"文件已转换为HTML格式，保存为 {output_file}")
        return output_file
    
    except Exception as e:
        print(f"转换文件 {input_file} 时出错: {str(e)}")
        return None

# 运行异步函数的入口点
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，转换指定文件
        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print(f"错误: 文件 {input_file} 不存在。")
            sys.exit(1)
            
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
            convert_md_to_html(input_file, output_file)
        else:
            convert_md_to_html(input_file)
    else:
        # 否则转换answer目录下的所有文件
        print("开始批量转换Markdown文件...")
        # 根据运行环境决定使用同步还是异步模式
        if os.name == 'nt':  # Windows
            convert_markdown_to_pdf_sync()
        else:  # Linux/Mac
            asyncio.run(convert_markdown_to_pdf())