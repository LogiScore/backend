Client Log

[Log] Build ID: build-1754957511634 - Timestamp: 1754957511634 - Version: v1754957511 - Hash: hash-s0s2978h1s (0.Cv8_sjbp.js, line 1)
[Log] Layout loaded with cache buster: – {timestamp: 1754957511634, id: "build-1754957511634", version: "v1754957511", …} (0.Cv8_sjbp.js, line 1)
{timestamp: 1754957511634, id: "build-1754957511634", version: "v1754957511", hash: "hash-s0s2978h1s", forceRebuild: true, …}Object
[Error] Origin http://logiscore.net is not allowed by Access-Control-Allow-Origin. Status code: 500
[Error] Fetch API cannot load https://logiscorebe.onrender.com/api/freight-forwarders/?limit=18&random_select=true due to access control checks.
[Error] Failed to load resource: Origin http://logiscore.net is not allowed by Access-Control-Allow-Origin. Status code: 500 (freight-forwarders, line 0)
[Error] Failed to fetch freight forwarders: – TypeError: Load failed
TypeError: Load failed
	(anonymous function) (D_fXWB-Q.js:1:1268)
[Error] Failed to load homepage data: – TypeError: Load failed
TypeError: Load failed
	(anonymous function) (2.Bk4qIaY1.js:1:4076)
[Warning] The resource http://logiscore.net/_app/immutable/assets/AuthModal.TNzN3L57.css was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/assets/SubscriptionModal.DTg4C3uo.css was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/assets/0.N1CHXiJ1.css was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/assets/2.D7NeZ5_U.css was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/entry/start.DCPR5_fg.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/BV1A3vsz.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/B_R0OAT9.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/C5vorxa-.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/BTISwQv_.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/n-QaIogt.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/entry/app.BkA3rDWB.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/DsnmJJEf.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/C2-vaxWA.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/CLMhcOLe.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.
[Warning] The resource http://logiscore.net/_app/immutable/chunks/LKPWIzj5.js was preloaded using link preload but not used within a few seconds from the window's load event. Please make sure it wasn't preloaded for nothing.

Render log

2025-08-12T00:11:51.674791962Z         self,
2025-08-12T00:11:51.674793642Z         distilled_parameters,
2025-08-12T00:11:51.674795342Z         execution_options or NO_OPTIONS,
2025-08-12T00:11:51.674796982Z     )
2025-08-12T00:11:51.674798642Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/sql/elements.py", line 526, in _execute_on_connection
2025-08-12T00:11:51.674803032Z     return connection._execute_clauseelement(
2025-08-12T00:11:51.674804762Z            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T00:11:51.674806432Z         self, distilled_params, execution_options
2025-08-12T00:11:51.674808042Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T00:11:51.674809682Z     )
2025-08-12T00:11:51.674811292Z     ^
2025-08-12T00:11:51.674812902Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1641, in _execute_clauseelement
2025-08-12T00:11:51.674814562Z     ret = self._execute_context(
2025-08-12T00:11:51.674816212Z         dialect,
2025-08-12T00:11:51.674817852Z     ...<8 lines>...
2025-08-12T00:11:51.674819492Z         cache_hit=cache_hit,
2025-08-12T00:11:51.674821142Z     )
2025-08-12T00:11:51.674822822Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1846, in _execute_context
2025-08-12T00:11:51.674824512Z     return self._exec_single_context(
2025-08-12T00:11:51.674826412Z            ~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T00:11:51.674828052Z         dialect, context, statement, parameters
2025-08-12T00:11:51.674829752Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T00:11:51.674831352Z     )
2025-08-12T00:11:51.674832963Z     ^
2025-08-12T00:11:51.674834693Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1986, in _exec_single_context
2025-08-12T00:11:51.674836393Z     self._handle_dbapi_exception(
2025-08-12T00:11:51.674838033Z     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T00:11:51.674839643Z         e, str_statement, effective_parameters, cursor, context
2025-08-12T00:11:51.674841263Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T00:11:51.674842873Z     )
2025-08-12T00:11:51.674844483Z     ^
2025-08-12T00:11:51.674846123Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 2355, in _handle_dbapi_exception
2025-08-12T00:11:51.674847883Z     raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
2025-08-12T00:11:51.674849563Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1967, in _exec_single_context
2025-08-12T00:11:51.674851273Z     self.dialect.do_execute(
2025-08-12T00:11:51.674852913Z     ~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T00:11:51.674861183Z         cursor, str_statement, effective_parameters, context
2025-08-12T00:11:51.674862953Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T00:11:51.674864603Z     )
2025-08-12T00:11:51.674866233Z     ^
2025-08-12T00:11:51.674867904Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/default.py", line 951, in do_execute
2025-08-12T00:11:51.674869633Z     cursor.execute(statement, parameters)
2025-08-12T00:11:51.674871264Z     ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T00:11:51.674872944Z sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column freight_forwarders.headquarters_country does not exist
2025-08-12T00:11:51.674874664Z LINE 1: ...rs.description AS freight_forwarders_description, freight_fo...
2025-08-12T00:11:51.674876314Z                                                              ^
2025-08-12T00:11:51.674877854Z 
2025-08-12T00:11:51.674880184Z [SQL: SELECT freight_forwarders.id AS freight_forwarders_id, freight_forwarders.name AS freight_forwarders_name, freight_forwarders.website AS freight_forwarders_website, freight_forwarders.logo_url AS freight_forwarders_logo_url, freight_forwarders.description AS freight_forwarders_description, freight_forwarders.headquarters_country AS freight_forwarders_headquarters_country, freight_forwarders.global_rank AS freight_forwarders_global_rank, freight_forwarders.is_active AS freight_forwarders_is_active, freight_forwarders.created_at AS freight_forwarders_created_at, freight_forwarders.updated_at AS freight_forwarders_updated_at, avg(reviews.overall_rating) AS avg_rating, count(reviews.id) AS review_count 
2025-08-12T00:11:51.674884634Z FROM freight_forwarders LEFT OUTER JOIN reviews ON freight_forwarders.id = reviews.freight_forwarder_id GROUP BY freight_forwarders.id]
2025-08-12T00:11:51.674886364Z (Background on this error at: https://sqlalche.me/e/20/f405)

Vercel log


AUG 12 08:11:51.20
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1754957480207, id: 'build-1754957480207', version: 'v1754957480', hash: 'hash-2gizv6rv32o', forceRebuild: true, noCache: true }
AUG 12 08:11:26.46
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1754957480207, id: 'build-1754957480207', version: 'v1754957480', hash: 'hash-2gizv6rv32o', forceRebuild: true, noCache: true }
AUG 12 08:11:22.82
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1754957480207, id: 'build-1754957480207', version: 'v1754957480', hash: 'hash-2gizv6rv32o', forceRebuild: true, noCache: true }
AUG 12 08:11:19.51
GET
200
logiscore.net
/
2
Layout loaded with cache buster: { timestamp: 1754957480207, id: 'build-1754957480207', version: 'v1754957480', hash: 'hash-2gizv6rv32o', forceRebuild: true, noCache: true }
