import app
from routes.personal import index
import cProfile
from pstats import Stats


def profile_request(path, cookie, f):
    a = app.configured_app()
    pr = cProfile.Profile()
    headers = {'Cookie': cookie}

    with a.test_request_context(path, headers=headers):
        pr.enable()
        f(7)
        pr.disable()

    pr.create_stats()
    s = Stats(pr).sort_stats('cumulative')
    s.dump_stats('profile.pstat')

    s.print_stats('.*Anfield.*')


if __name__ == '__main__':
    path = '/personal/7'
    cookie = 'cache_session=user78f2482d-92c5-4923-8b79-0e890d432b78'
    profile_request(path, cookie, index)
