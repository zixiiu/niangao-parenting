# 年糕宝宝早教活动页面

🦞 由小龙虾自动生成的年糕宝宝每日早教活动页面

## 📋 页面内容

- **宝宝年龄**：自动计算天龄和月龄
- **发育里程碑**：根据国家卫健委指南提供本月龄发育标志
- **5个早教活动**：基于权威来源的适龄早教游戏
- **特殊日子提醒**：百日、周岁、节气等
- **温馨提示**：科学育儿建议

## 🚀 部署到 GitHub Pages

### 方法1：使用环境变量

```bash
export GITHUB_TOKEN='your_github_token'
bash deploy.sh
```

### 方法2：创建token文件

```bash
mkdir -p ~/.config/niangao
echo 'your_github_token' > ~/.config/niangao/github_token
bash deploy.sh
```

### 方法3：命令行参数

```bash
bash deploy.sh --token 'your_github_token'
```

## 🔑 创建 GitHub Token

1. 访问：https://github.com/settings/tokens/new
2. 选择权限：`repo`（完整仓库访问权限）
3. 描述：`niangao-parenting-deploy`
4. 点击 "Generate token"
5. 复制生成的 token

## 📚 数据来源

- 国家卫生健康委《婴幼儿早期发展服务指南（试行）》（2024）
- 中国幼教网《0-3岁早教方案》
- 豆瓣亲子教育专栏

## 🎯 今日活动（2026-03-02）

1. 黑白卡视觉追踪训练
2. 俯卧抬头练习
3. 面对面注视与交流
4. 听声转头训练
5. 亲子抚触按摩

## 📊 宝宝信息

- **姓名**：年糕
- **出生日期**：2026年1月9日
- **今日年龄**：52天（1.7个月）
- **百日倒计时**：48天

## 🌐 在线访问

部署成功后访问：https://zixiiu.github.io/niangao-parenting/

---

🦞 小龙虾 | OpenClaw Agent
