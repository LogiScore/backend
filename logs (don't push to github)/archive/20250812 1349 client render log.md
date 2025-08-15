client log

[Log] Build ID: build-1754977791067 - Timestamp: 1754977791067 - Version: v1754977791 - Hash: hash-w1mq7bio8zk (0.Cv8_sjbp.js, line 1)
[Log] Layout loaded with cache buster: – Object (0.Cv8_sjbp.js, line 1)
Object
[Error] Origin https://logiscore-frontend.vercel.app is not allowed by Access-Control-Allow-Origin. Status code: 500
[Error] Fetch API cannot load https://logiscorebe.onrender.com/api/freight-forwarders/?limit=18&random_select=true due to access control checks.
[Error] Failed to load resource: Origin https://logiscore-frontend.vercel.app is not allowed by Access-Control-Allow-Origin. Status code: 500 (freight-forwarders, line 0)
[Error] Failed to fetch freight forwarders: – TypeError: Load failed
TypeError: Load failed
	(anonymous function) (D_fXWB-Q.js:1:1268)
[Error] Failed to load homepage data: – TypeError: Load failed
TypeError: Load failed
	(anonymous function) (2.Bk4qIaY1.js:1:4076)

render log

2025-08-12T05:49:51.232092438Z         self,
2025-08-12T05:49:51.232095058Z         distilled_parameters,
2025-08-12T05:49:51.232097618Z         execution_options or NO_OPTIONS,
2025-08-12T05:49:51.232100078Z     )
2025-08-12T05:49:51.232102618Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 526, in _execute_on_connection
2025-08-12T05:49:51.232105088Z     return connection._execute_clauseelement(
2025-08-12T05:49:51.232107748Z            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.232110268Z         self, distilled_params, execution_options
2025-08-12T05:49:51.232112728Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232115258Z     )
2025-08-12T05:49:51.232117688Z     ^
2025-08-12T05:49:51.232120198Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1641, in _execute_clauseelement
2025-08-12T05:49:51.232122828Z     ret = self._execute_context(
2025-08-12T05:49:51.232125419Z         dialect,
2025-08-12T05:49:51.232127888Z     ...<8 lines>...
2025-08-12T05:49:51.232130379Z         cache_hit=cache_hit,
2025-08-12T05:49:51.232132849Z     )
2025-08-12T05:49:51.232135559Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1846, in _execute_context
2025-08-12T05:49:51.232142689Z     return self._exec_single_context(
2025-08-12T05:49:51.232145409Z            ~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.232147879Z         dialect, context, statement, parameters
2025-08-12T05:49:51.232150349Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232152869Z     )
2025-08-12T05:49:51.232155369Z     ^
2025-08-12T05:49:51.232157859Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1986, in _exec_single_context
2025-08-12T05:49:51.232160409Z     self._handle_dbapi_exception(
2025-08-12T05:49:51.232162849Z     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.232165429Z         e, str_statement, effective_parameters, cursor, context
2025-08-12T05:49:51.2321679Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232170469Z     )
2025-08-12T05:49:51.23217305Z     ^
2025-08-12T05:49:51.23217557Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 2355, in _handle_dbapi_exception
2025-08-12T05:49:51.23217811Z     raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
2025-08-12T05:49:51.23218069Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1967, in _exec_single_context
2025-08-12T05:49:51.23218323Z     self.dialect.do_execute(
2025-08-12T05:49:51.23218577Z     ~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.23218834Z         cursor, str_statement, effective_parameters, context
2025-08-12T05:49:51.23220403Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232206961Z     )
2025-08-12T05:49:51.232229391Z     ^
2025-08-12T05:49:51.232236351Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 951, in do_execute
2025-08-12T05:49:51.232239321Z     cursor.execute(statement, parameters)
2025-08-12T05:49:51.232241861Z     ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232244871Z sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column reviews.overall_rating does not exist
2025-08-12T05:49:51.232247441Z LINE 1: ....updated_at AS freight_forwarders_updated_at, avg(reviews.ov...
2025-08-12T05:49:51.232250102Z                                                              ^
2025-08-12T05:49:51.232252391Z 
2025-08-12T05:49:51.232257342Z [SQL: SELECT freight_forwarders.id AS freight_forwarders_id, freight_forwarders.name AS freight_forwarders_name, freight_forwarders.website AS freight_forwarders_website, freight_forwarders.logo_url AS freight_forwarders_logo_url, freight_forwarders.description AS freight_forwarders_description, freight_forwarders.headquarters_country AS freight_forwarders_headquarters_country, freight_forwarders.global_rank AS freight_forwarders_global_rank, freight_forwarders.is_active AS freight_forwarders_is_active, freight_forwarders.created_at AS freight_forwarders_created_at, freight_forwarders.updated_at AS freight_forwarders_updated_at, avg(reviews.overall_rating) AS avg_rating, count(reviews.id) AS review_count 
2025-08-12T05:49:51.232260212Z FROM freight_forwarders LEFT OUTER JOIN reviews ON freight_forwarders.id = reviews.freight_forwarder_id GROUP BY freight_forwarders.id]
2025-08-12T05:49:51.232262842Z (Background on this error at: https://sqlalche.me/e/20/f405)