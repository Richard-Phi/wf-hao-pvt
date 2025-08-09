use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Write};
use anyhow::{Result, Context};

// 存储单字编码的结构
#[derive(Debug)]
struct CharCode {
    char: char,
    code: String,
}

// 添加新的结构来存储词条信息
#[derive(Debug)]
struct WordEntry {
    word: String,
    weight: Option<String>,
}

fn main() -> Result<()> {
    // 读取单字码表
    let char_codes = load_char_codes("data/单字全码表.txt")?;
    
    // 创建字符到编码的映射
    let char_to_code: HashMap<char, String> = char_codes
        .into_iter()
        .map(|cc| (cc.char, cc.code))
        .collect();

    let input_file = File::open("../../deploy/hao/多字词.txt")
        .context("无法打开词语文件")?;
    let reader = BufReader::new(input_file);
    
    let mut output = File::create("data/output.txt")
        .context("无法创建输出文件")?;
    let mut error_output = File::create("data/errors.txt")
        .context("无法创建错误日志文件")?;

    for line in reader.lines() {
        let line = line?.trim().to_string();
        if line.is_empty() {
            continue;
        }

        match parse_word_entry(&line) {
            Ok(entry) => {
                let chars: Vec<char> = entry.word.chars().collect();
                match generate_code(&chars, &char_to_code) {
                    Ok(code) => {
                        // 输出格式为：词语\t编码\t词频
                        // 如果有权重值则使用，否则使用默认值0.0099990000
                        let weight = entry.weight.unwrap_or("0.0099990000".to_string());
                        writeln!(output, "{}\t{}\t{}", entry.word, code, weight)?;
                    }
                    Err(e) => {
                        writeln!(error_output, "{}\t{}", entry.word, e)?;
                    }
                }
            }
            Err(e) => {
                writeln!(error_output, "解析错误: {}\t{}", line, e)?;
            }
        }
    }

    Ok(())
}

fn load_char_codes(path: &str) -> Result<Vec<CharCode>> {
    let content = fs::read_to_string(path)
        .context("无法读取单字码表文件")?;
    
    let mut char_codes = Vec::new();
    for line in content.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.is_empty() {
            continue;
        }
        
        // 确保至少有字符和编码两列
        if parts.len() >= 2 {
            let char = parts[0].chars().next()
                .context("无效的字符")?;
            char_codes.push(CharCode {
                char,
                code: parts[1].to_string(),
            });
        }
    }
    Ok(char_codes)
}

fn parse_word_entry(line: &str) -> Result<WordEntry> {
    let parts: Vec<&str> = line.split_whitespace().collect();
    if parts.is_empty() {
        return Err(anyhow::anyhow!("空行"));
    }

    Ok(WordEntry {
        word: parts[0].to_string(),
        weight: parts.get(1).map(|s| s.to_string()),
    })
}

// 从编码字符串中提取大写字母序列
fn extract_uppercase_sequence(code: &str) -> String {
    code.chars().filter(|c| c.is_uppercase()).collect()
}

// 获取序列的前n个字符（不足则取全部）
fn take_first_n(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

// 获取整个编码的最后一码
fn get_last_code_char(code: &str) -> char {
    code.chars().last().unwrap_or(' ')
}

fn generate_two_char_code(
    chars: &[char],
    char_to_code: &HashMap<char, String>
) -> Result<String> {
    let first_code = get_char_code(chars[0], char_to_code)?;
    let second_code = get_char_code(chars[1], char_to_code)?;
    
    let first_upper = extract_uppercase_sequence(&first_code);
    let second_upper = extract_uppercase_sequence(&second_code);
    
    if first_upper.is_empty() {
        return Err(anyhow::anyhow!("第一个字没有大写字母编码"));
    }
    if second_upper.is_empty() {
        return Err(anyhow::anyhow!("第二个字没有大写字母编码"));
    }
    
    // 取第一字的前2个大写字母（第1和第2个大写字母）
    let first_part = take_first_n(&first_upper, 2);
    // 取第二字的前2个大写字母（第1和第2个大写字母）
    let second_part = take_first_n(&second_upper, 2);
    // 取第二字的末码（整个编码的最后一码）
    let last_of_second = get_last_code_char(&second_code);
    
    Ok(format!("{}{}{}", first_part, second_part, last_of_second))
}

fn generate_three_char_code(
    chars: &[char],
    char_to_code: &HashMap<char, String>
) -> Result<String> {
    let first_code = get_char_code(chars[0], char_to_code)?;
    let second_code = get_char_code(chars[1], char_to_code)?;
    let third_code = get_char_code(chars[2], char_to_code)?;
    
    let first_upper = extract_uppercase_sequence(&first_code);
    let second_upper = extract_uppercase_sequence(&second_code);
    let third_upper = extract_uppercase_sequence(&third_code);
    
    if first_upper.is_empty() {
        return Err(anyhow::anyhow!("第一个字没有大写字母编码"));
    }
    if second_upper.is_empty() {
        return Err(anyhow::anyhow!("第二个字没有大写字母编码"));
    }
    if third_upper.is_empty() {
        return Err(anyhow::anyhow!("第三个字没有大写字母编码"));
    }
    
    // 取每个字的第一个大写字母
    let first_char = first_upper.chars().next().unwrap();
    let second_char = second_upper.chars().next().unwrap();
    let third_char = third_upper.chars().next().unwrap();
    // 取第三字的末码（整个编码的最后一码）
    let last_of_third = get_last_code_char(&third_code);
    
    Ok(format!("{}{}{}{}", first_char, second_char, third_char, last_of_third))
}

fn generate_four_char_code(
    chars: &[char],
    char_to_code: &HashMap<char, String>
) -> Result<String> {
    let first_code = get_char_code(chars[0], char_to_code)?;
    let second_code = get_char_code(chars[1], char_to_code)?;
    let third_code = get_char_code(chars[2], char_to_code)?;
    let fourth_code = get_char_code(chars[3], char_to_code)?;
    
    let first_upper = extract_uppercase_sequence(&first_code);
    let second_upper = extract_uppercase_sequence(&second_code);
    let third_upper = extract_uppercase_sequence(&third_code);
    let fourth_upper = extract_uppercase_sequence(&fourth_code);
    
    if first_upper.is_empty() {
        return Err(anyhow::anyhow!("第一个字没有大写字母编码"));
    }
    if second_upper.is_empty() {
        return Err(anyhow::anyhow!("第二个字没有大写字母编码"));
    }
    if third_upper.is_empty() {
        return Err(anyhow::anyhow!("第三个字没有大写字母编码"));
    }
    if fourth_upper.is_empty() {
        return Err(anyhow::anyhow!("第四个字没有大写字母编码"));
    }
    
    // 取前四个字的第一个大写字母
    let first_char = first_upper.chars().next().unwrap();
    let second_char = second_upper.chars().next().unwrap();
    let third_char = third_upper.chars().next().unwrap();
    let fourth_char = fourth_upper.chars().next().unwrap();
    // 取第四字的末码（整个编码的最后一码）
    let last_of_fourth = get_last_code_char(&fourth_code);
    
    Ok(format!("{}{}{}{}{}", first_char, second_char, third_char, fourth_char, last_of_fourth))
}

fn generate_five_plus_char_code(
    chars: &[char],
    char_to_code: &HashMap<char, String>
) -> Result<String> {
    // 获取前三字的大写字母序列
    let first_upper = extract_uppercase_sequence(&get_char_code(chars[0], char_to_code)?);
    let second_upper = extract_uppercase_sequence(&get_char_code(chars[1], char_to_code)?);
    let third_upper = extract_uppercase_sequence(&get_char_code(chars[2], char_to_code)?);
    
    // 获取末字
    let last_char = chars[chars.len()-1];
    let last_code = get_char_code(last_char, char_to_code)?;
    let last_upper = extract_uppercase_sequence(&last_code);
    
    // 检查大写字母序列是否为空
    if first_upper.is_empty() || second_upper.is_empty() || third_upper.is_empty() || last_upper.is_empty() {
        return Err(anyhow::anyhow!("存在没有大写字母编码的字"));
    }
    
    // 取前三字的第一个大写字母
    let first_char = first_upper.chars().next().unwrap();
    let second_char = second_upper.chars().next().unwrap();
    let third_char = third_upper.chars().next().unwrap();
    // 取末字的第一个大写字母
    let last_first_char = last_upper.chars().next().unwrap();
    // 取末字的末码（整个编码的最后一码）
    let last_of_last = get_last_code_char(&last_code);
    
    Ok(format!("{}{}{}{}{}", first_char, second_char, third_char, last_first_char, last_of_last))
}

fn get_char_code(c: char, char_to_code: &HashMap<char, String>) -> Result<String> {
    char_to_code
        .get(&c)
        .cloned()
        .context(format!("找不到字符'{}'的编码", c))
}

fn generate_code(chars: &[char], char_to_code: &HashMap<char, String>) -> Result<String> {
    match chars.len() {
        2 => generate_two_char_code(chars, char_to_code),
        3 => generate_three_char_code(chars, char_to_code),
        4 => generate_four_char_code(chars, char_to_code),
        n if n >= 5 => generate_five_plus_char_code(chars, char_to_code),
        _ => Err(anyhow::anyhow!("词语长度小于2")),
    }
}