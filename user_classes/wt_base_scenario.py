from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, generationFlightsDates
import random
from urllib.parse import unquote_plus


class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)

    test_users_csv_file_path = './test_data/user_data_test.csv'
    test_typeSeat_csv_file_path = './test_data/typeSeat.csv'
    test_users_data = open_csv_field(test_users_csv_file_path)
    test_type_seat = open_csv_field(test_typeSeat_csv_file_path)

    def on_start(self) -> None:

        @task
        def uc_01_01_getHomePage(self) -> None:
            self.client.get(
                '/WebTours',
                name='REQ_01_01_1_/WebTours/',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                # debug_stream = sys.stderr
            )

            self.client.get(
                '/cgi-bin/welcome.pl?signOff=1',
                name='REQ_01_01_2_/cgi-bin/welcome.pl?signOff=1',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                #debug_stream = sys.stderr
            )

            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name='REQ_01_01_3_/cgi-bin/nav.pl?in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                #debug_stream = sys.stderr
            ) as req_01_3_response:
                check_http_response(req_01_3_response, "name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req_01_3_response.text).group(1)

        @task
        def uc_01_02_getLlogin(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)
            self.userName = self.user_data_row['username']
            self.password = self.user_data_row['password']
            req_body_01_02 = f'userSession={self.userSession}&username={self.userName}&password={self.password}&login.x=42&login.y=5&JSFormSubmit=off'

            with self.client.post(
                '/cgi-bin/login.pl',
                name='REQ_01_02_1_/cgi-bin/login.pl/',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_01_02,
                catch_response=True,
                # debug_stream = sys.stderr
            ) as req_01_02_response:
                check_http_response(req_01_02_response, "User password was correct")

            self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='REQ_01_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                # debug_stream = sys.stderr
            )

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ_01_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'accept-Encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    debug_stream=sys.stderr
            ) as req_01_3_response:
                check_http_response(req_01_3_response, f"Welcome, <b>{self.userName}</b>, to the Web Tours reservation pages.")

        uc_01_01_getHomePage(self)
        uc_01_02_getLlogin(self)

    @task
    def uc_01_03_openFlight(self):
        self.client.get(
            '/cgi-bin/welcome.pl?page=search',
            name='REQ_01_03_1_/cgi-bin/welcome.pl?page=search',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-Encoding': 'gzip, deflate, br, zstd'
            },
            # debug_stream = sys.stderr
        )

        self.client.get(
            '/cgi-bin/nav.pl?page=menu&in=flights',
            name='REQ_01_03_2_/cgi-bin/nav.pl?page=menu&in=flights',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-Encoding': 'gzip, deflate, br, zstd'
            },
            allow_redirects=False,
            # debug_stream = sys.stderr
        )

        with self.client.get(
            '/cgi-bin/reservations.pl?page=welcome',
            name='REQ_01_03_3_/cgi-bin/reservations.pl?page=welcome',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-Encoding': 'gzip, deflate, br, zstd'
            },
            allow_redirects=False,
            catch_response=True,
            # debug_stream = sys.stderr
        ) as req_03_3_response:
            check_http_response(req_03_3_response, "Flight Selections")

    @task
    def uc_01_04_findFlight(self):
        self.seat_data_row = random.choice(self.test_type_seat)
        self.seatType = self.seat_data_row['seatType']
        self.seatPref = self.seat_data_row['seatPref']
        self.depart = self.user_data_row['depart']
        self.arrive = self.user_data_row['arrive']
        date_list = generationFlightsDates()

        req_body_04_01 = f'advanceDiscount=0&depart={self.depart}&departDate={date_list["depart_date"]}&arrive={self.arrive}&returnDate={date_list["arrive_date"]}&numPassengers=1&seatPref={self.seatPref}&seatType={self.seatType}&findFlights.x=49&findFlights.y=1&.cgifields=roundtrip&.cgifields=seatType&.cgifields=seatPref'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ_01_04_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_04_01,
                catch_response=True,
                #debug_stream = sys.stderr
        ) as req_04_1_response:
            check_http_response(req_04_1_response, "name=\"outboundFlight\"")

        self.outboundFlight = re.search(r'name=\"outboundFlight\" value=\"(.*)\">', req_04_1_response.text).group(1)
        print(f'НАЙДЕН ПАРАМЕТР - {self.outboundFlight}')

    @task
    def uc_01_05_choiceFlight(self):

        req_body_05_01 = f'outboundFlight={unquote_plus(self.outboundFlight)}&numPassengers=1&advanceDiscount=0&seatType={self.seatType}&seatPref={self.seatPref}&reserveFlights.x=47&reserveFlights.y=9'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ_01_05_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_05_01,
                catch_response=True,
                #debug_stream=sys.stderr
        ) as req_05_1_response:
            check_http_response(req_05_1_response, "Flight Reservation")

    @task
    def uc_01_06_paymentFlight(self):
        self.creditCard = self.seat_data_row['creditCard']
        self.expDate = self.seat_data_row['expDate']
        self.address1 = self.user_data_row['address1']
        self.address2 = self.user_data_row['address2']
        self.pass1 = self.user_data_row['pass1']

        req_body_06_01 = f'firstName={self.userName}&lastName={self.password}&address1={self.address1}&address2={self.address2}&pass1={self.pass1}&creditCard={self.creditCard}&expDate={self.expDate}&oldCCOption=&numPassengers=1&seatType={self.seatType}&seatPref={self.seatPref}&outboundFlight={unquote_plus(self.outboundFlight)}&advanceDiscount=0&returnFlight=&JSFormSubmit=off&buyFlights.x=37&buyFlights.y=10&.cgifields=saveCC'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ_01_06_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_06_01,
                catch_response=True,
                debug_stream = sys.stderr
        ) as req_06_1_response:
            check_http_response(req_06_1_response, f"from {self.depart} to {self.arrive}.</u></b>")



class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]