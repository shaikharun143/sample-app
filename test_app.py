from	app	import	app

def	test_home():
  res	=	app.test_client().get("/")
  assert	res.status_code	==	200
  assert	b"Hello"	in	res.data
  
def	test_health():
  res	=	app.test_client().get("/health")
  assert	res.status_code	==	200
