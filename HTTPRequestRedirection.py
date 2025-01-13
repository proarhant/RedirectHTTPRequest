def lambda_handler(event, context):
    # ######################################################################################################################################
    #
    # Author:          Provungshu Arhant
    # Lambda Function: HTTPRequestRedirection.py
    # Description:     AWS Lambda@Edge function to redirect CloudFront HTTP requests based on the request headers.
    # Purpose:
    #                  Unwanted traffic that are not from allowed geo-locations( e.g. UK, SG) gets blocked and then redirected to a page. 
    #                  Valid traffic are returned without manipulating the original web request and send it to the CloudFront origin.
    #
    # ######################################################################################################################################
    
    '''
    To block any invalid traffic, the following five (05) vars are used to compare against the geo-location specific request:
        1)  The allowedGeoLocations contains the geo-locations that are allowed to access the sensitiveUriList.
        2)  The sensitiveUriList contains the path to be allowed only for the valid HTTP requests.
        3)  The allowedClientIpList contains the allowed IPs of the clients that can access the sensitiveUriList.
        4)  The allowedSessionCookie contains the session cookie name that confirms any valid HTTP request.
        5)  The customBlockPage contains the URL of the landing page for invalid HTTP requests.
    '''

    allowedGeoLocations = ["UK", "SG]"
    sensitiveUriList = ["/myPersonalData", "/myProfile", "/purchase-history"]
    #Allowed client IP list
    allowedClientIpList = ["125.132.32.23", "221.56.36.88", "232.121.56.79"]
    allowedSessionCookie = "ALOW_MY_SESSION"
    customBlockPage = 'https://block.gokates.io'

    #The logic below will now use the above variables to crontol whether to block or allow traffic.

    #request = event["Records"][0]["cf"]["request"] #This is the HTTP request format for CloudFront CDN
    request = event #This is for offline testing passed from main function
    
    print(request)
    
    try:
        # Try-catch block to check and capture any invalid record(s) in the CDN request
        print("The number of records in the request:", len(request)) if len(request) == 7 else print("The request may NOT be valid.")
        # For live execution, the following line will be uncommented.
        #print("Invoker: ", context.invoked_function_arn, " Log Stream Name: ", context.log_stream_name)

        # Header Values are being validated using 'validateThenAssign' function to avoid unexpected termination of the lambda function
        headers         = request["headers"]
        # countryCode   = headers["cloudfront-viewer-country"][0]["value"]
        countryCode     = validateThenAssign(headers, "cloudfront-viewer-country", "value")
        # userAgent     = headers["user-agent"][0]["value"]
        userAgent       = validateThenAssign(headers, "user-agent", "value")    
        # host          = headers["host"][0]["value"]
        host            = validateThenAssign(headers, "host", "value")
        # domainName    = request["origin"]["custom"]["domainName"]
        domainName      = validateThenAssign(request, "origin", "custom")

        # Variables from request which are under the try-catch block
        uri = request["uri"]
        clientIp = request["clientIp"]
        queryString     = request['querystring']
        
    except Exception as e:
        # Lets not manipulate the request, and lets send the original request to the origin.
        # Variables (countryCode, userAgent, host and domainName) are validated and assigned in the child try-catch block.
        # Catch exception and print the error message for the rest of the code (e.g. uri, clientIP, etc), and let the code continue execution.
        print("Main:Try:Except block:", e, type(e).__name__)
    else:
        # Lets not manipulate the request, and lets send the original request to the origin
        # Variables are validated and assigned in the child try-catch block
        print("The request has expected format for the origin.")
    finally:
        # Lets not manipulate the request. Return original request to the origin.
        print("The code execution for invalidation and assignment is completed for the origin.")
        print("userAgent ", userAgent)
        userAgent = "" if userAgent is None else userAgent #Assign an empty string to userAgent to avoid warning.
        sourceIsMobile = ("iPhone" in userAgent or ("Android" in userAgent and "Mobile" in userAgent))
        print("sourceIsMobile ", sourceIsMobile)

    # Cookie Variables are being compared against WebAppSessionCookie = "Allow_MyApp_SESSION_Private"
    parsedCookies = parseCookies(headers)
    
    '''
    # These sample values will block all traffic from geo-locations other than those lised in allowedGeoLocations.
    uri = "myProfile"
    countryCode = "RU"
    clientIp = "245.22.245.212"
    clientIp = None
    allowedSessionCookie = "Allow_MyApp_SESSION_Private"
    '''

    #The if statement decides whether to block or allow HTTP traffic coming to CDN.
    print("uri", uri, "   countryCode", countryCode, "   clientIp", clientIp, "   host", host, "   domainName", domainName, "   allowedSessionCookie", allowedSessionCookie, "   redirectedURL", customBlockPage)
    # Block all HTTP Traffic not from the UK geo location
    # sensitiveUriList = ["/myPersonalData", "/myProfile", "/purchase-history"]
    #if (uri == "/myProfile" or uri == "/myPersonalData" or uri == "/myProfile" or uri == "/purchase-history") and countryCode != "JP" and clientIp not in clientIpList and checkCookie(parsedCookies, allowedSessionCookie) is False:
    #if uri in sensitiveUriList and countryCode != "UK" and clientIp not in allowedClientIpList and checkCookie(parsedCookies, allowedSessionCookie) is False:
    if uri in sensitiveUriList and countryCode not in allowedGeoLocations and clientIp not in allowedClientIpList and checkCookie(parsedCookies, allowedSessionCookie) is False:
        response = {
            'status': '302',
            'statusDescription': 'Found',
            'headers': {
                'location': [{
                    'key': 'Location',
                    'value': customBlockPage
                }]
            }
        }

        print("Blocked all non UK Traffic")
        print("response ", response)

        return response

    # Return original request to the origin if no match found.
    print("Match not found, so returning original response to origin")
    request['headers']['host'] = [{'key': 'host', 'value': domainName}]
    return request

def checkCookie(parsedCookies, cookie):
#     cookiePresent = (parsedCookies and cookie in parsedCookies)
#     return bool(cookiePresent) is False or cookiePresent is False
    return cookie in parsedCookies

def parseCookies(headers):
    parsedCookie = {}
    if headers.get('cookie'):
        for cookie in headers['cookie'][0]['value'].split(';'):
            if cookie:
                parts = cookie.split('=')
                parsedCookie[parts[0].strip()] = parts[1].strip()
    return parsedCookie

def validateThenAssign(dict, cacheKey, key):
    #Lets not manipulate the request. In this def, we do condition checks and then send the original request to the origin.
    #   countryCode   = headers["cloudfront-viewer-country"][0]["value"]
    #   countryCode   = validateThenAssign(headers, "cloudfront-viewer-country", "value")
    #   domainName    = request["origin"]["custom"]["domainName"]
    #   domainName    = validateThenAssign(request, "origin", "custom")
    try:
       #The following three statements may be invoked in the future e.g. usecases captured in the logs     
       #dict[cacheKey]
       #dict[cacheKey] if cacheKey == "origin" else dict[cacheKey][0][key]
       #dict[cacheKey][key]["domainName"] if cacheKey == "origin" else dict[cacheKey][0][key]
       (v := dict[cacheKey][0][key]) if cacheKey != "origin" else (v := dict[cacheKey][key]["domainName"])
       #While None is dealt in the expection block, the following code is to catch other exceptions
       if not type(v) is str:
          raise TypeError(f"RAISE:warning: {cacheKey} has type mismatch. Expected string, but got {type(v).__name__}.")
       if v.strip() == "":
          raise Exception(f"RAISE:warning: {cacheKey} has empty value for the key {key}.")
    except Exception as e:
       #Lets not manipulate the request, and in this block, we are catching exceptions and let the code continue execution.
       #print("Nested Key", {key},"does NOT exist in headers[",cacheKey,"]")
       print("Child:Try:Except block:", "Nested Key", {key}, "does NOT exist.", e, "Error type:", type(e).__name__)
       #pass
       #Do not return anything, as we are not manipulating the request. Do not raise exception unless the caller try-catch needs to catch this raise.
       #raise Exception(f"RAISE: Child:Try:Except block: Nested Key {key} does NOT exist. {e}  {type(e).__name__}")
    else:
       print(f"Child:Try:Else block: Nested Key \"{key}\" exists in {dict[cacheKey]}")
       #return dict[cacheKey][0][key] if cacheKey != "origin" else dict[cacheKey][key]["domainName"]
       return v
   
def main():
    print("")
    print("Offiline code execution for this py file.")
    print("Invoking this function from main!")
    request_type_1 = {'body': {'action': 'read-only', 'data': '', 'encoding': 'base64', 'inputTruncated': False}, 'clientIp': '218.219.168.196', 'headers': {'host': [{'key': 'Host', 'value': 'k8s.gokates'}], 'referer': [{'key': 'Referer', 'value': 'https://k8s.gokates/login'}], 'x-forwarded-for': [{'key': 'X-Forwarded-For', 'value': '218.219.168.196'}], 'user-agent': [{'key': 'User-Agent', 'value': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}], 'via': [{'key': 'Via', 'value': '1.1 70545c8d6.cloudfront.net (CloudFront)'}], 'accept-encoding': [{'key': 'Accept-Encoding', 'value': 'br,gzip'}], 'cloudfront-viewer-country': [{'key': 'CloudFront-Viewer-Country', 'value': 'JP'}]}, 'method': 'GET', 'origin': {'custom': {'customHeaders': {}, 'domainName': 'gokates-io.s3.amazonaws.com', 'keepaliveTimeout': 5, 'path': '', 'port': 443, 'protocol': 'https', 'readTimeout': 30, 'sslProtocols': ['TLSv1', 'SSLv3']}}, 'querystring': '', 'uri': '/songs/serial.mp3'}
    request_type_2 = {'body': {'action': 'read-only', 'data': '', 'encoding': 'base64', 'inputTruncated': False}, 'clientIp': '34.116.22.33', 'headers': {'host': [{'key': 'Host', 'value': 'k8s.gokates'}], 'x-forwarded-for': [{'key': 'X-Forwarded-For', 'value': '34.116.22.33'}], 'user-agent': [{'key': 'User-Agent', 'value': 'Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: UAEmdDd94DTaX2A-vxySHC2TVdUA6-G3YIg)'}], 'via': [{'key': 'Via', 'value': '1.1 3e05889c1fb3e37dfed25cc0ce3f3b72.cloudfront.net (CloudFront)'}], 'accept-encoding': [{'key': 'Accept-Encoding', 'value': 'br,gzip'}]}, 'method': 'GET', 'origin': {'custom': {'customHeaders': {}, 'domainName': 'gokates-io.s3.amazonaws.com', 'keepaliveTimeout': 5, 'path': '', 'port': 443, 'protocol': 'https', 'readTimeout': 30, 'sslProtocols': ['TLSv1', 'SSLv3']}}, 'querystring': '', 'uri': '/index.html'}
    request_type_3 = {'body': {'action': 'read-only', 'data': '', 'encoding': 'base64', 'inputTruncated': False}, 'clientIp': '34.116.22.33', 'headers': {'host': [{'key': 'Host', 'value': 'k8s.gokates'}], 'x-forwarded-for': [{'key': 'X-Forwarded-For', 'value': '34.116.22.33'}], 'user-agent': [{'key': 'User-Agent', 'value': 'Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: UAEmdDd94DTaX2A-vxySHC2TVdUA6-G3YIg)'}], 'via': [{'key': 'Via', 'value': '1.1 3e05889c1fb3e37dfed25cc0ce3f3b72.cloudfront.net (CloudFront)'}], 'accept-encoding': [{'key': 'Accept-Encoding', 'value': 'br,gzip'}]}, 'method': 'GET', 'origin': {'custom': {'customHeaders': {}, 'domainName': 'gokates-io.s3.amazonaws.com', 'keepaliveTimeout': 5, 'path': '', 'port': 443, 'protocol': 'https', 'readTimeout': 30, 'sslProtocols': ['TLSv1', 'SSLv3']}}, 'querystring': '', 'uri': '/'}
    
    print("This event value is the CloudFront HTTP request that will be checked by this function.")
    print("")
    event = request_type_3

    lambda_handler(event, "context")

if __name__ == "__main__":
    main()
