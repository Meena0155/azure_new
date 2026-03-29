# import azure.functions as func
# from function1 import bp1
# from function2 import bp2

# # Note: Using AuthLevel.ANONYMOUS because we will use 
# # Azure AD (App Service Auth) for Managed Identity security.
# app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# app.register_functions(bp1)
# app.register_functions(bp2)

import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# 1. Keep the Hello function so you know it's working
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("I am alive!")

# 2. Wrap the imports in a try-except to see the error
try:
    from function1 import bp1
    app.register_functions(bp1)
    logging.info("Function1 registered successfully")
except Exception as e:
    logging.error(f"Failed to load Function1: {str(e)}")

try:
    from function2 import bp2
    app.register_functions(bp2)
    logging.info("Function2 registered successfully")
except Exception as e:
    logging.error(f"Failed to load Function2: {str(e)}")