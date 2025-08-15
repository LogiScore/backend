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
2025-08-12T06:01:58.768114134Z ==> Deploying...
2025-08-12T06:02:20.696388605Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2025-08-12T06:02:25.008632622Z Traceback (most recent call last):
2025-08-12T06:02:25.008653513Z   File "/opt/render/project/src/.venv/bin/uvicorn", line 8, in <module>
2025-08-12T06:02:25.008663983Z     sys.exit(main())
2025-08-12T06:02:25.008704464Z              ^^^^^^
2025-08-12T06:02:25.008708324Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
2025-08-12T06:02:25.008963281Z     return self.main(*args, **kwargs)
2025-08-12T06:02:25.008985822Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.008996012Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1363, in main
2025-08-12T06:02:25.00928243Z     rv = self.invoke(ctx)
2025-08-12T06:02:25.00928926Z          ^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.00929198Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
2025-08-12T06:02:25.009503335Z     return ctx.invoke(self.callback, **ctx.params)
2025-08-12T06:02:25.009513825Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.009516905Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 794, in invoke
2025-08-12T06:02:25.009767072Z     return callback(*args, **kwargs)
2025-08-12T06:02:25.009792623Z            ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.009796783Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 413, in main
2025-08-12T06:02:25.009969097Z     run(
2025-08-12T06:02:25.009980538Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 580, in run
2025-08-12T06:02:25.010116591Z     server.run()
2025-08-12T06:02:25.010125541Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
2025-08-12T06:02:25.010222184Z     return asyncio.run(self.serve(sockets=sockets))
2025-08-12T06:02:25.010265055Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.010271275Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 190, in run
2025-08-12T06:02:25.010389498Z     return runner.run(main)
2025-08-12T06:02:25.010395179Z            ^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.010398319Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 118, in run
2025-08-12T06:02:25.010497111Z     return self._loop.run_until_complete(task)
2025-08-12T06:02:25.010517912Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.010521162Z   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
2025-08-12T06:02:25.010688136Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
2025-08-12T06:02:25.010759168Z     await self._serve(sockets)
2025-08-12T06:02:25.010795129Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
2025-08-12T06:02:25.010917282Z     config.load()
2025-08-12T06:02:25.010934673Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 436, in load
2025-08-12T06:02:25.011095827Z     self.loaded_app = import_from_string(self.app)
2025-08-12T06:02:25.011111047Z                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.011116617Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
2025-08-12T06:02:25.0111955Z     module = importlib.import_module(module_str)
2025-08-12T06:02:25.01120793Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.01122218Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-12T06:02:25.011323343Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-12T06:02:25.011353373Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:25.011356074Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-12T06:02:25.011357934Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-12T06:02:25.011359634Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-12T06:02:25.011361324Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-12T06:02:25.011365204Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-12T06:02:25.011366934Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-12T06:02:25.011368604Z   File "/opt/render/project/src/main.py", line 17, in <module>
2025-08-12T06:02:25.011462956Z     from routes import users, freight_forwarders, reviews, search, subscriptions
2025-08-12T06:02:25.011465847Z   File "/opt/render/project/src/routes/reviews.py", line 8, in <module>
2025-08-12T06:02:25.011547639Z     from ..database.database import get_db
2025-08-12T06:02:25.011553439Z ImportError: attempted relative import beyond top-level package
2025-08-12T06:02:34.276246736Z ==> Exited with status 1
2025-08-12T06:02:34.439364317Z ==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
2025-08-12T06:02:35.579209767Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2025-08-12T06:02:39.782891049Z Traceback (most recent call last):
2025-08-12T06:02:39.78290925Z   File "/opt/render/project/src/.venv/bin/uvicorn", line 8, in <module>
2025-08-12T06:02:39.782974772Z     sys.exit(main())
2025-08-12T06:02:39.783015813Z              ^^^^^^
2025-08-12T06:02:39.783019833Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1442, in __call__
2025-08-12T06:02:39.783243759Z     return self.main(*args, **kwargs)
2025-08-12T06:02:39.78327815Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.78328231Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1363, in main
2025-08-12T06:02:39.783508986Z     rv = self.invoke(ctx)
2025-08-12T06:02:39.783535106Z          ^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.783539126Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 1226, in invoke
2025-08-12T06:02:39.783821134Z     return ctx.invoke(self.callback, **ctx.params)
2025-08-12T06:02:39.783844534Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.783849525Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/click/core.py", line 794, in invoke
2025-08-12T06:02:39.78404948Z     return callback(*args, **kwargs)
2025-08-12T06:02:39.78405342Z            ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.78405536Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 413, in main
2025-08-12T06:02:39.784191903Z     run(
2025-08-12T06:02:39.784198194Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 580, in run
2025-08-12T06:02:39.784285866Z     server.run()
2025-08-12T06:02:39.784291166Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
2025-08-12T06:02:39.784356128Z     return asyncio.run(self.serve(sockets=sockets))
2025-08-12T06:02:39.784372028Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.784377738Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 190, in run
2025-08-12T06:02:39.784473251Z     return runner.run(main)
2025-08-12T06:02:39.784477571Z            ^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.784480461Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/asyncio/runners.py", line 118, in run
2025-08-12T06:02:39.784546603Z     return self._loop.run_until_complete(task)
2025-08-12T06:02:39.784552943Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.784555823Z   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
2025-08-12T06:02:39.784670426Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
2025-08-12T06:02:39.784728408Z     await self._serve(sockets)
2025-08-12T06:02:39.784731137Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
2025-08-12T06:02:39.7848299Z     config.load()
2025-08-12T06:02:39.78484098Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 436, in load
2025-08-12T06:02:39.784959503Z     self.loaded_app = import_from_string(self.app)
2025-08-12T06:02:39.784963123Z                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.784968524Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
2025-08-12T06:02:39.785048906Z     module = importlib.import_module(module_str)
2025-08-12T06:02:39.785065936Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.785081997Z   File "/opt/render/project/python/Python-3.11.9/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-12T06:02:39.785127508Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-12T06:02:39.785165309Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-12T06:02:39.785167969Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-12T06:02:39.785169759Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-12T06:02:39.785171489Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-12T06:02:39.785173129Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-12T06:02:39.785183609Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-12T06:02:39.78518554Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-12T06:02:39.78518968Z   File "/opt/render/project/src/main.py", line 17, in <module>
2025-08-12T06:02:39.785273762Z     from routes import users, freight_forwarders, reviews, search, subscriptions
2025-08-12T06:02:39.785277642Z   File "/opt/render/project/src/routes/reviews.py", line 8, in <module>
2025-08-12T06:02:39.785368584Z     from ..database.database import get_db
2025-08-12T06:02:39.785371824Z ImportError: attempted relative import beyond top-level package