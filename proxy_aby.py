# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "HP73A503KW30F0BD"
proxyPass = "D31BA3031DC2C4DA"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

#clash 代理
proxyMeta2 = "127.0.0.1:7890"

proxies = {
    "http": proxyMeta2,
    "https": proxyMeta2,
}