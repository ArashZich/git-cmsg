# change_analyzer.py

import os
import subprocess
import sys
import re

def analyze_staged_changes(staged_files):
    """
    تحلیل تغییرات فایل‌های stage شده و ارائه پیشنهاد برای نوع، محدوده و موضوع کامیت
    
    Args:
        staged_files (list): لیست فایل‌های stage شده
        
    Returns:
        dict: دیکشنری شامل نوع، محدوده و موضوع پیشنهادی برای کامیت
    """
    # بررسی اینکه آیا تغییرات شامل فایل‌های جدید است یا خیر
    new_files = [f for f in staged_files if check_if_new_file(f)]
    
    # بررسی نوع محتوای فایل‌ها
    file_types = analyze_file_types(staged_files)
    
    # تحلیل تغییرات برای تشخیص نوع کامیت
    changes_analysis = analyze_file_changes(staged_files)
    
    # تعیین نوع کامیت بر اساس تحلیل‌ها
    suggested_type = determine_commit_type(new_files, file_types, changes_analysis)
    
    # پیشنهاد محدوده بر اساس ساختار فایل‌ها
    suggested_scope = determine_commit_scope(staged_files)
    
    # پیشنهاد موضوع کامیت بر اساس تغییرات و محتوا
    suggested_subject = determine_commit_subject(new_files, file_types, changes_analysis, suggested_type)
    
    return {
        'type': suggested_type,
        'scope': suggested_scope,
        'subject': suggested_subject
    }

def analyze_file_types(staged_files):
    """تحلیل نوع فایل‌ها بر اساس پسوند و محتوا"""
    file_types = {
        'python': 0,  # .py
        'document': 0,  # .md, .txt, etc.
        'config': 0,  # .json, .yaml, .ini, etc.
        'style': 0,  # .css, .scss, etc.
        'script': 0,  # .sh, .js, etc.
        'test': 0,  # test_ files
        'ui': 0,  # UI related files
        'data': 0,  # .csv, .xml, etc.
    }
    
    for file_path in staged_files:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Check Python files
        if ext == '.py':
            file_types['python'] += 1
            # Check if it's a test file
            if 'test_' in filename or '_test' in filename or 'tests/' in file_path:
                file_types['test'] += 2  # Give higher weight to test files
        
        # Check document files
        elif ext in ['.md', '.txt', '.rst', '.adoc']:
            file_types['document'] += 1
            
        # Check config files
        elif ext in ['.json', '.yaml', '.yml', '.ini', '.toml', '.conf']:
            file_types['config'] += 1
            
        # Check style files
        elif ext in ['.css', '.scss', '.less', '.sass']:
            file_types['style'] += 1
            
        # Check script files
        elif ext in ['.sh', '.bash', '.js', '.ts']:
            file_types['script'] += 1
            
        # Check data files
        elif ext in ['.csv', '.xml', '.json', '.sql']:
            file_types['data'] += 1
            
        # Check if file is likely UI related
        if 'ui' in file_path.lower() or 'interface' in file_path.lower() or 'view' in file_path.lower():
            file_types['ui'] += 1
    
    return file_types

def analyze_file_changes(staged_files):
    """تحلیل تغییرات در فایل‌ها برای تشخیص نوع عملیات"""
    analysis = {
        'total_additions': 0,
        'total_deletions': 0,
        'file_operations': [],  # اطلاعات تغییرات هر فایل
        'change_type': 'neutral'  # 'add', 'remove', 'modify', یا 'neutral'
    }
    
    for file_path in staged_files:
        additions, deletions = get_diff_stats(file_path)
        is_new = check_if_new_file(file_path)
        
        analysis['total_additions'] += additions
        analysis['total_deletions'] += deletions
        
        # تعیین نوع تغییر برای هر فایل
        if is_new:
            file_op = 'add'
        elif deletions > additions * 2:
            file_op = 'remove'
        elif additions > deletions * 2:
            file_op = 'enhance'
        else:
            file_op = 'modify'
            
        analysis['file_operations'].append({
            'path': file_path,
            'operation': file_op,
            'additions': additions,
            'deletions': deletions,
            'is_new': is_new
        })
    
    # تعیین نوع کلی تغییرات
    if analysis['total_additions'] > 0 and analysis['total_deletions'] == 0:
        analysis['change_type'] = 'add'
    elif analysis['total_deletions'] > 0 and analysis['total_additions'] == 0:
        analysis['change_type'] = 'remove'
    elif analysis['total_additions'] > analysis['total_deletions'] * 2:
        analysis['change_type'] = 'enhance'
    elif analysis['total_deletions'] > analysis['total_additions'] * 2:
        analysis['change_type'] = 'refactor'
    else:
        analysis['change_type'] = 'modify'
        
    return analysis

def determine_commit_type(new_files, file_types, changes_analysis):
    """تعیین نوع کامیت بر اساس تحلیل‌های مختلف"""
    # وزن‌دهی برای هر نوع کامیت بر اساس تحلیل‌ها
    type_weights = {
        'feat': 0,
        'fix': 0,
        'docs': 0,
        'style': 0,
        'refactor': 0,
        'test': 0,
        'chore': 0
    }
    
    # افزایش وزن بر اساس فایل‌های جدید
    if len(new_files) > 0:
        if len(new_files) == len(changes_analysis['file_operations']):
            # اگر همه فایل‌ها جدید باشند
            type_weights['feat'] += 3
        else:
            # اگر برخی فایل‌ها جدید باشند
            type_weights['feat'] += 2
    
    # افزایش وزن بر اساس نوع فایل‌ها
    if file_types['document'] > 0:
        type_weights['docs'] += file_types['document'] * 2
    
    if file_types['test'] > 0:
        type_weights['test'] += file_types['test'] * 2
    
    if file_types['style'] > 0:
        type_weights['style'] += file_types['style'] * 2
    
    if file_types['config'] > 0:
        type_weights['chore'] += file_types['config']
    
    # افزایش وزن بر اساس نوع تغییرات
    if changes_analysis['change_type'] == 'add':
        type_weights['feat'] += 2
    elif changes_analysis['change_type'] == 'remove':
        type_weights['refactor'] += 2
    elif changes_analysis['change_type'] == 'enhance':
        type_weights['feat'] += 1
        type_weights['fix'] += 1
    elif changes_analysis['change_type'] == 'refactor':
        type_weights['refactor'] += 3
    elif changes_analysis['change_type'] == 'modify':
        type_weights['fix'] += 2
    
    # بررسی پسوند فایل‌ها برای تشخیص نوع تغییرات
    for file_op in changes_analysis['file_operations']:
        filepath = file_op['path']
        # بررسی اگر فایل به تست‌ها مربوط است
        if 'test' in filepath or 'spec' in filepath:
            type_weights['test'] += 1
        # بررسی اگر فایل به داکیومنت مربوط است
        elif 'doc' in filepath or 'README' in filepath or 'CHANGELOG' in filepath:
            type_weights['docs'] += 1
        # بررسی اگر فایل به استایل مربوط است
        elif 'style' in filepath or 'css' in filepath:
            type_weights['style'] += 1
        # بررسی اگر فایل به تنظیمات مربوط است
        elif 'config' in filepath or '.json' in filepath or '.yml' in filepath:
            type_weights['chore'] += 1
    
    # تعیین نوع کامیت با بیشترین وزن
    max_weight = 0
    suggested_type = 'feat'  # پیش‌فرض
    
    for type_name, weight in type_weights.items():
        if weight > max_weight:
            max_weight = weight
            suggested_type = type_name
    
    # اگر نتوانستیم به یک نتیجه مشخص برسیم
    if max_weight == 0:
        # برای حالت‌های خاص
        if len(changes_analysis['file_operations']) <= 3:
            # برای تغییرات کوچک
            suggested_type = 'fix'
        else:
            # برای تغییرات بزرگ‌تر
            suggested_type = 'feat'
    
    return suggested_type

def determine_commit_scope(staged_files):
    """تعیین محدوده کامیت بر اساس ساختار فایل‌ها"""
    # جمع‌آوری اطلاعات مسیر فایل‌ها
    directories = {}
    
    for file_path in staged_files:
        parts = os.path.normpath(file_path).split(os.sep)
        
        # بررسی دایرکتوری اصلی
        if len(parts) > 1 and parts[0]:
            dir_name = parts[0]
            directories[dir_name] = directories.get(dir_name, 0) + 1
    
    # اگر همه فایل‌ها در یک دایرکتوری هستند
    if len(directories) == 1 and len(directories) == len(staged_files):
        return next(iter(directories.keys()))
    
    # اگر بیشتر فایل‌ها در یک دایرکتوری هستند
    if directories:
        max_dir = max(directories.items(), key=lambda x: x[1])
        if max_dir[1] >= len(staged_files) * 0.5:  # اگر حداقل 50٪ فایل‌ها در این دایرکتوری باشند
            return max_dir[0]
    
    # اگر فقط یک فایل داریم
    if len(staged_files) == 1:
        filename = os.path.splitext(os.path.basename(staged_files[0]))[0]
        # اگر نام فایل معنادار باشد
        if len(filename) <= 15 and not filename.startswith('.'):
            return filename
    
    # تلاش برای پیدا کردن یک محدوده معنادار از نام فایل‌ها
    common_prefixes = find_common_prefix(staged_files)
    if common_prefixes:
        return common_prefixes[0]
    
    # اگر نتوانستیم محدوده مناسبی پیدا کنیم
    return ""

def find_common_prefix(file_paths):
    """پیدا کردن پیشوند مشترک در نام فایل‌ها"""
    filenames = [os.path.basename(path) for path in file_paths]
    
    # حذف پسوندها
    names_without_ext = [os.path.splitext(name)[0] for name in filenames]
    
    # پیدا کردن پیشوندهای مشترک
    prefixes = []
    
    for name in names_without_ext:
        for i in range(3, len(name) + 1):
            prefix = name[:i].lower()
            if len(prefix) < 3:  # پیشوندهای خیلی کوتاه را نادیده بگیر
                continue
                
            prefix_count = sum(1 for n in names_without_ext if n.lower().startswith(prefix))
            
            if prefix_count >= len(names_without_ext) * 0.5:  # اگر حداقل 50٪ فایل‌ها این پیشوند را داشته باشند
                prefixes.append((prefix, prefix_count))
    
    # مرتب‌سازی بر اساس تعداد تطابق و طول پیشوند
    prefixes.sort(key=lambda x: (-x[1], len(x[0])))
    
    return [p[0] for p in prefixes[:3]] if prefixes else []

def determine_commit_subject(new_files, file_types, changes_analysis, commit_type):
    """تعیین موضوع کامیت براساس تحلیل‌ها و نوع کامیت"""
    # لیست پیشنهادات مناسب برای هر نوع کامیت
    subject_templates = {
        'feat': [
            "add {feature} functionality",
            "implement {feature} feature",
            "create new {feature}",
            "add support for {feature}",
            "introduce {feature} capabilities"
        ],
        'fix': [
            "fix {issue} issue",
            "correct {issue} problem",
            "resolve {issue} bug",
            "address {issue} error",
            "fix issue with {issue}"
        ],
        'docs': [
            "update {doc} documentation",
            "improve {doc} docs",
            "document {doc} feature",
            "add {doc} documentation",
            "clarify {doc} usage"
        ],
        'style': [
            "improve {style} formatting",
            "update {style} styles",
            "standardize {style} formatting",
            "clean up {style} code",
            "apply consistent styling to {style}"
        ],
        'refactor': [
            "refactor {code} for better readability",
            "simplify {code} logic",
            "restructure {code} architecture",
            "improve {code} code organization",
            "optimize {code} implementation"
        ],
        'test': [
            "add tests for {function}",
            "improve test coverage for {function}",
            "fix failing tests in {function}",
            "add unit tests for {function}",
            "implement integration tests for {function}"
        ],
        'chore': [
            "update {config} dependencies",
            "configure {config} settings",
            "maintain {config} infrastructure",
            "update project configuration",
            "automate {config} process"
        ]
    }
    
    # تعیین کلمه کلیدی مناسب برای استفاده در الگوها
    keyword = ""
    
    # تعیین کلمه کلیدی بر اساس نوع فایل
    if file_types['python'] > 0:
        keyword = "Python"
    elif file_types['document'] > 0:
        keyword = "documentation"
    elif file_types['config'] > 0:
        keyword = "configuration"
    elif file_types['style'] > 0:
        keyword = "style"
    elif file_types['test'] > 0:
        keyword = "testing"
    elif file_types['ui'] > 0:
        keyword = "user interface"
    elif file_types['data'] > 0:
        keyword = "data processing"
    
    # اگر نتوانستیم از نوع فایل تشخیص دهیم، از نام فایل استفاده می‌کنیم
    if not keyword and len(changes_analysis['file_operations']) <= 2:
        # استفاده از نام فایل برای کلمه کلیدی
        filename = os.path.splitext(os.path.basename(changes_analysis['file_operations'][0]['path']))[0]
        if not filename.startswith('.') and len(filename) <= 20:
            keyword = filename
    
    # اگر هنوز کلمه کلیدی نداریم، از نوع تغییرات استفاده می‌کنیم
    if not keyword:
        if changes_analysis['change_type'] == 'add':
            keyword = "new feature"
        elif changes_analysis['change_type'] == 'remove':
            keyword = "unnecessary code"
        elif changes_analysis['change_type'] == 'enhance':
            keyword = "existing functionality"
        elif changes_analysis['change_type'] == 'refactor':
            keyword = "codebase"
        else:
            keyword = "code"
    
    # انتخاب یک الگوی تصادفی و جایگزینی کلمه کلیدی
    import random
    templates = subject_templates.get(commit_type, subject_templates['feat'])
    template = random.choice(templates)
    
    # جایگزینی کلمه کلیدی در الگو
    suggested_subject = template.format(
        feature=keyword, 
        issue=keyword, 
        doc=keyword, 
        style=keyword, 
        code=keyword, 
        function=keyword, 
        config=keyword
    )
    
    return suggested_subject

def check_if_new_file(file_path):
    """بررسی می‌کند که آیا فایل جدید است یا خیر"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-status', file_path],
            check=False,
            capture_output=True,
            text=True
        )
        # 'A' نشان‌دهنده فایل جدید است
        return result.stdout.strip().startswith('A')
    except Exception:
        return False

def get_diff_stats(file_path):
    """تعداد خطوط اضافه و حذف شده را محاسبه می‌کند"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--numstat', file_path],
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return 0, 0
            
        # خروجی به صورت "additions    deletions    file_path" است
        numbers = result.stdout.strip().split(None, 2)
        if len(numbers) >= 2:
            try:
                return int(numbers[0]), int(numbers[1])
            except ValueError:
                return 0, 0
        return 0, 0
    except Exception as e:
        print(f"Error getting diff stats: {e}", file=sys.stderr)
        return 0, 0