2025-08-12T05:49:51.231826151Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
2025-08-12T05:49:51.231828681Z     return await self.app(scope, receive, send)
2025-08-12T05:49:51.231831141Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.231833681Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/applications.py", line 1054, in __call__
2025-08-12T05:49:51.231836212Z     await super().__call__(scope, receive, send)
2025-08-12T05:49:51.231838632Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/applications.py", line 113, in __call__
2025-08-12T05:49:51.231841282Z     await self.middleware_stack(scope, receive, send)
2025-08-12T05:49:51.231843832Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/errors.py", line 186, in __call__
2025-08-12T05:49:51.231846622Z     raise exc
2025-08-12T05:49:51.231849102Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/errors.py", line 164, in __call__
2025-08-12T05:49:51.231851622Z     await self.app(scope, receive, _send)
2025-08-12T05:49:51.231854192Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/cors.py", line 93, in __call__
2025-08-12T05:49:51.231856652Z     await self.simple_response(scope, receive, send, request_headers=headers)
2025-08-12T05:49:51.231859192Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/cors.py", line 144, in simple_response
2025-08-12T05:49:51.231862122Z     await self.app(scope, receive, send)
2025-08-12T05:49:51.231864632Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
2025-08-12T05:49:51.231872232Z     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
2025-08-12T05:49:51.231874973Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-08-12T05:49:51.231877553Z     raise exc
2025-08-12T05:49:51.231880062Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-08-12T05:49:51.231882593Z     await app(scope, receive, sender)
2025-08-12T05:49:51.231885683Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 716, in __call__
2025-08-12T05:49:51.231888293Z     await self.middleware_stack(scope, receive, send)
2025-08-12T05:49:51.231890963Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 736, in app
2025-08-12T05:49:51.231893443Z     await route.handle(scope, receive, send)
2025-08-12T05:49:51.231895953Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 290, in handle
2025-08-12T05:49:51.231898443Z     await self.app(scope, receive, send)
2025-08-12T05:49:51.231900943Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 78, in app
2025-08-12T05:49:51.231903433Z     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
2025-08-12T05:49:51.231909043Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-08-12T05:49:51.231911753Z     raise exc
2025-08-12T05:49:51.231914333Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-08-12T05:49:51.231916794Z     await app(scope, receive, sender)
2025-08-12T05:49:51.231919314Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/starlette/routing.py", line 75, in app
2025-08-12T05:49:51.231921863Z     response = await f(request)
2025-08-12T05:49:51.231933004Z                ^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.231936784Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 302, in app
2025-08-12T05:49:51.231940124Z     raw_response = await run_endpoint_function(
2025-08-12T05:49:51.231942874Z                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.231946054Z     ...<3 lines>...
2025-08-12T05:49:51.231948704Z     )
2025-08-12T05:49:51.231951294Z     ^
2025-08-12T05:49:51.231954324Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 213, in run_endpoint_function
2025-08-12T05:49:51.231957015Z     return await dependant.call(**values)
2025-08-12T05:49:51.231959655Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.231962344Z   File "/opt/render/project/src/routes/freight_forwarders.py", line 64, in get_freight_forwarders
2025-08-12T05:49:51.231965105Z     all_results = query.group_by(FreightForwarder.id).all()
2025-08-12T05:49:51.231967765Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2704, in all
2025-08-12T05:49:51.231970445Z     return self._iter().all()  # type: ignore
2025-08-12T05:49:51.231973155Z            ~~~~~~~~~~^^
2025-08-12T05:49:51.231983195Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/query.py", line 2857, in _iter
2025-08-12T05:49:51.231986595Z     result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
2025-08-12T05:49:51.231989305Z                                                   ~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.231991925Z         statement,
2025-08-12T05:49:51.232000176Z         ^^^^^^^^^^
2025-08-12T05:49:51.232003125Z         params,
2025-08-12T05:49:51.232005756Z         ^^^^^^^
2025-08-12T05:49:51.232008266Z         execution_options={"_sa_orm_load_options": self.load_options},
2025-08-12T05:49:51.232011126Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232013756Z     )
2025-08-12T05:49:51.232016426Z     ^
2025-08-12T05:49:51.232019266Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 2365, in execute
2025-08-12T05:49:51.232022056Z     return self._execute_internal(
2025-08-12T05:49:51.232024596Z            ~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.232027236Z         statement,
2025-08-12T05:49:51.232029856Z         ^^^^^^^^^^
2025-08-12T05:49:51.232032566Z     ...<4 lines>...
2025-08-12T05:49:51.232035396Z         _add_event=_add_event,
2025-08-12T05:49:51.232038186Z         ^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:49:51.232040986Z     )
2025-08-12T05:49:51.232043657Z     ^
2025-08-12T05:49:51.232046606Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/session.py", line 2251, in _execute_internal
2025-08-12T05:49:51.232049377Z     result: Result[Any] = compile_state_cls.orm_execute_statement(
2025-08-12T05:49:51.232052207Z                           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
2025-08-12T05:49:51.232054967Z         self,
2025-08-12T05:49:51.232057837Z         ^^^^^
2025-08-12T05:49:51.232060767Z     ...<4 lines>...
2025-08-12T05:49:51.232064567Z         conn,
2025-08-12T05:49:51.232067777Z         ^^^^^
2025-08-12T05:49:51.232070847Z     )
2025-08-12T05:49:51.232074017Z     ^
2025-08-12T05:49:51.232076817Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/orm/context.py", line 306, in orm_execute_statement
2025-08-12T05:49:51.232079407Z     result = conn.execute(
2025-08-12T05:49:51.232081987Z         statement, params or {}, execution_options=execution_options
2025-08-12T05:49:51.232084498Z     )
2025-08-12T05:49:51.232087207Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/sqlalchemy/engine/base.py", line 1419, in execute
2025-08-12T05:49:51.232089838Z     return meth(
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
2025-08-12T05:53:51.205850904Z ==> Deploying...
2025-08-12T05:54:12.836761887Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2025-08-12T05:54:18.234855206Z Traceback (most recent call last):
2025-08-12T05:54:18.234870827Z   File "/opt/render/project/src/.venv/bin/uvicorn", line 8, in <module>
2025-08-12T05:54:18.234913137Z     sys.exit(main())
2025-08-12T05:54:18.234916017Z              ^^^^^^
2025-08-12T05:54:18.234918788Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
2025-08-12T05:54:18.235173334Z     return self.main(*args, **kwargs)
2025-08-12T05:54:18.235187124Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.235191754Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1363, in main
2025-08-12T05:54:18.235398059Z     rv = self.invoke(ctx)
2025-08-12T05:54:18.235402719Z          ^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.235406749Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
2025-08-12T05:54:18.235631445Z     return ctx.invoke(self.callback, **ctx.params)
2025-08-12T05:54:18.235636405Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.235640075Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 794, in invoke
2025-08-12T05:54:18.235789219Z     return callback(*args, **kwargs)
2025-08-12T05:54:18.235797949Z            ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.235801789Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 413, in main
2025-08-12T05:54:18.235910872Z     run(
2025-08-12T05:54:18.235915642Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 580, in run
2025-08-12T05:54:18.236041345Z     server.run()
2025-08-12T05:54:18.236051265Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
2025-08-12T05:54:18.236153247Z     return asyncio.run(self.serve(sockets=sockets))
2025-08-12T05:54:18.236161588Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.236163928Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 190, in run
2025-08-12T05:54:18.23627078Z     return runner.run(main)
2025-08-12T05:54:18.23627472Z            ^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.23627697Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 118, in run
2025-08-12T05:54:18.236360072Z     return self._loop.run_until_complete(task)
2025-08-12T05:54:18.236369103Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.236376283Z   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
2025-08-12T05:54:18.236513456Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
2025-08-12T05:54:18.236566077Z     await self._serve(sockets)
2025-08-12T05:54:18.236571677Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
2025-08-12T05:54:18.2366608Z     config.load()
2025-08-12T05:54:18.23666565Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 436, in load
2025-08-12T05:54:18.236765162Z     self.loaded_app = import_from_string(self.app)
2025-08-12T05:54:18.236773652Z                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.236776702Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
2025-08-12T05:54:18.236857214Z     module = importlib.import_module(module_str)
2025-08-12T05:54:18.236863815Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.236876975Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-12T05:54:18.236943626Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-12T05:54:18.236971477Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:18.236974147Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-12T05:54:18.236975907Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-12T05:54:18.236977597Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-12T05:54:18.236979257Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-12T05:54:18.236980887Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-12T05:54:18.236982497Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-12T05:54:18.236998608Z   File "/opt/render/project/src/main.py", line 15, in <module>
2025-08-12T05:54:18.23708061Z     from database.models import Base
2025-08-12T05:54:18.2370908Z   File "/opt/render/project/src/database/models.py", line 2, in <module>
2025-08-12T05:54:18.237168312Z     from sqlalchemy.orm import relationship, hybrid_property
2025-08-12T05:54:18.237175972Z ImportError: cannot import name 'hybrid_property' from 'sqlalchemy.orm' (/opt/render/project/src/.venv/lib/python3.11/site-packages/sqlalchemy/orm/__init__.py)
2025-08-12T05:54:23.216683344Z ==> Exited with status 1
2025-08-12T05:54:23.376890546Z ==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
2025-08-12T05:54:24.325157392Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2025-08-12T05:54:28.858073036Z Traceback (most recent call last):
2025-08-12T05:54:28.858089467Z   File "/opt/render/project/src/.venv/bin/uvicorn", line 8, in <module>
2025-08-12T05:54:28.858138738Z     sys.exit(main())
2025-08-12T05:54:28.858141408Z              ^^^^^^
2025-08-12T05:54:28.858145558Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
2025-08-12T05:54:28.858388244Z     return self.main(*args, **kwargs)
2025-08-12T05:54:28.858393954Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.858398794Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1363, in main
2025-08-12T05:54:28.858608809Z     rv = self.invoke(ctx)
2025-08-12T05:54:28.858614369Z          ^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.858618229Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
2025-08-12T05:54:28.858800914Z     return ctx.invoke(self.callback, **ctx.params)
2025-08-12T05:54:28.858813924Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.858817804Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 794, in invoke
2025-08-12T05:54:28.858975538Z     return callback(*args, **kwargs)
2025-08-12T05:54:28.858982758Z            ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.858985669Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 413, in main
2025-08-12T05:54:28.859128992Z     run(
2025-08-12T05:54:28.859136692Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 580, in run
2025-08-12T05:54:28.859250325Z     server.run()
2025-08-12T05:54:28.859255615Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
2025-08-12T05:54:28.859328287Z     return asyncio.run(self.serve(sockets=sockets))
2025-08-12T05:54:28.859336357Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.859339357Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 190, in run
2025-08-12T05:54:28.85944158Z     return runner.run(main)
2025-08-12T05:54:28.8594445Z            ^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.85944644Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 118, in run
2025-08-12T05:54:28.859520391Z     return self._loop.run_until_complete(task)
2025-08-12T05:54:28.859526451Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.859528631Z   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
2025-08-12T05:54:28.859644364Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
2025-08-12T05:54:28.859696976Z     await self._serve(sockets)
2025-08-12T05:54:28.859711436Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
2025-08-12T05:54:28.859788818Z     config.load()
2025-08-12T05:54:28.859791778Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 436, in load
2025-08-12T05:54:28.859899751Z     self.loaded_app = import_from_string(self.app)
2025-08-12T05:54:28.859904161Z                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.859906601Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
2025-08-12T05:54:28.859979302Z     module = importlib.import_module(module_str)
2025-08-12T05:54:28.859993963Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.860009233Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-12T05:54:28.90127846Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-12T05:54:28.9012959Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T05:54:28.90130085Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-12T05:54:28.901304451Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-12T05:54:28.901313441Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-12T05:54:28.901317021Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-12T05:54:28.901320891Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-12T05:54:28.901324331Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-12T05:54:28.901327451Z   File "/opt/render/project/src/main.py", line 15, in <module>
2025-08-12T05:54:28.901420573Z     from database.models import Base
2025-08-12T05:54:28.901428783Z   File "/opt/render/project/src/database/models.py", line 2, in <module>
2025-08-12T05:54:28.901510625Z     from sqlalchemy.orm import relationship, hybrid_property
2025-08-12T05:54:28.901515285Z ImportError: cannot import name 'hybrid_property' from 'sqlalchemy.orm' (/opt/render/project/src/.venv/lib/python3.11/site-packages/sqlalchemy/orm/__init__.py)