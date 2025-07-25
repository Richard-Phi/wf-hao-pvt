package tools

import (
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"gen_sy/types"
)

var (
	// 文件内容缓存
	fileCache     = make(map[string][]byte)
	fileCacheLock sync.RWMutex
)

// 读取文件内容，带缓存功能
func readFileWithCache(filepath string) ([]byte, error) {
	fileCacheLock.RLock()
	content, exists := fileCache[filepath]
	fileCacheLock.RUnlock()
	
	if exists {
		return content, nil
	}
	
	content, err := os.ReadFile(filepath)
	if err != nil {
		return nil, err
	}
	
	fileCacheLock.Lock()
	fileCache[filepath] = content
	fileCacheLock.Unlock()
	
	return content, nil
}

func ReadDivisionTable(filepath string) (table map[string][]*types.Division, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	matcher := regexp.MustCompile("{.*?}|.")
	table = map[string][]*types.Division{}
	for _, line := range strings.Split(string(buffer), "\n") {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		// 的\t[白勹丶,de_dī_dí_dì,CJK,U+7684]
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		if len(line) < 2 {
			continue
		}
		// [白勹丶,de_dī_dí_dì,CJK,U+7684]
		meta := strings.Split(strings.Trim(line[1], "[]"), ",")
		if len(meta) < 4 {
			continue
		}
		div := types.Division{
			Char: line[0],
			Divs: matcher.FindAllString(meta[0], -1),
			Pin:  meta[1],
			Set:  meta[2],
			Unicode: meta[3],
		}
		if len(div.Divs) == 0 {
			continue
		}
		table[div.Char] = append(table[div.Char], &div)
	}

	return
}

func ReadCharSimpTable(filepath string) (table map[string][]*types.CharSimp, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	table = map[string][]*types.CharSimp{}
	for _, line := range strings.Split(string(buffer), "\n") {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		simp := types.CharSimp{
			Char: line[0],
			Simp: line[1],
		}
		table[simp.Char] = append(table[simp.Char], &simp)
	}

	return
}

func ReadCompMap(filepath string) (mappings map[string]string, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	mappings = map[string]string{}
	for _, line := range strings.Split(string(buffer), "\n") {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		code, comp := strings.ReplaceAll(line[0], "_", "1"), line[1]
		mappings[comp] = code
	}

	return
}

func ReadCharFreq(filepath string) (freqSet map[string]int64, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	freqSet = map[string]int64{}
	for _, line := range strings.Split(string(buffer), "\n") {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		char, freqStr := line[0], line[1]
		freq, _ := strconv.ParseFloat(freqStr, 64)
		freqSet[char] = int64(freq * 1e8)
	}

	return
}

func ReadPhraseFreq(filepath string) (freqSet map[string]int64, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	freqSet = map[string]int64{}
	lines := strings.Split(string(buffer), "\n")
	for i, line := range lines {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		// phrase, freqStr := line[0], line[1]
		// freqSet[phrase], _ = strconv.ParseInt(freqStr, 10, 64)
		phrase := line[0]
		if _, ok := freqSet[phrase]; !ok {
			freqSet[phrase] = int64(len(lines) - i)
		}
	}

	return
}

func ReadCJKExtWhitelist(filepath string) (whitelist map[rune]bool, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	whitelist = map[rune]bool{}
	lines := strings.Split(string(buffer), "\n")
	for _, line := range lines {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		char := strings.SplitN(strings.TrimRight(line, "\r\n"), "\t", 1)[0]
		if len(char) == 0 {
			continue
		}
		whitelist[[]rune(char)[0]] = true
	}

	return
}

// ReadStrokeTable 读取笔画表
func ReadStrokeTable(filepath string) (table map[string]string, err error) {
	buffer, err := readFileWithCache(filepath)
	if err != nil {
		return
	}

	table = map[string]string{}
	for _, line := range strings.Split(string(buffer), "\n") {
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		// 格式：汉字\t笔画序列
		line := strings.Split(strings.TrimRight(line, "\r\n"), "\t")
		if len(line) < 2 {
			continue
		}
		
		// 存储汉字及其笔画序列
		table[line[0]] = line[1]
	}

	return
}
