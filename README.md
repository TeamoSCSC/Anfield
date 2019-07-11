论坛地址： http://www.teamodou.com  欢迎访问！


## 基于Flask的个人论坛
数据存储使用MySQL，ORM使用SQLAlchemy，模板使用Jinja2，使用Redis进行缓存优化。

**主要功能**

- 用户注册与登陆、论坛首页以及个人主页；
- 支持用户个人信息修改，如个性签名、头像设置等；
- 多板块，支持话题的发布、删除、评论及搜索；
- 用户间私信功能，并支持@用户功能；
- 密码重置功能，使用个人邮箱找回密码。

**安全与优化**

- 利用 Token 实现对 CSRF 攻击的防御；
- 使用转义防止 XSS、SQL 注入；
- 使用摘要和加盐对密码进行存储，保证用户密码安全；
- 使用服务器端 Session 实现当前用户验证；
- Session 和 Token 使用 Redis 进行存储，以支持多进程间数据共享。

**项目部署**

- 使用  Nginx 进行反向代理，过滤静态资源请求；
- 使用 Supervisor 守护进程；
- 使用 Gunicorn 多worker + gevent 协程架构，实现负载均衡。

## 演示
**登录与话题操作**

![](https://github.com/TeamoSCSC/Anfield/blob/master/images/login.gif)

**板块筛选与话题查找**

![](https://github.com/TeamoSCSC/Anfield/blob/master/images/search.gif)

**用户编辑**

![](https://github.com/TeamoSCSC/Anfield/blob/master/images/edit.gif)

**密码找回**

![](https://github.com/TeamoSCSC/Anfield/blob/master/images/reset.gif)

**私信**

![](https://github.com/TeamoSCSC/Anfield/blob/master/images/chat.gif)