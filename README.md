# RedirectHTTPRequest
AWS Lambda@Edge function to redirect CloudFront HTTP requests based on the request headers.

# What This Lambda@Edge Function Does?
    ########################################################################################################################################
    #
    # Author:          Provungshu Arhant
    # Lambda Function: HTTPRequestRedirection.py
    # Description:     AWS Lambda@Edge function to redirect CloudFront HTTP requests based on the request headers.
    # Purpose:
    #                  Unwanted traffic that are not from allowed geo-locations( e.g. UK, SG) gets blocked and then redirected to a page. 
    #                  Valid traffic are returned without manipulating the original web request and send it to the CloudFront origin.
    #
    ########################################################################################################################################
    
    To block any invalid traffic, the following five (05) vars are used to compare against the geo-location specific request:
        1)  The allowedGeoLocations contains the geo-locations that are allowed to access the sensitiveUriList.
        2)  The sensitiveUriList contains the path to be allowed only for the valid HTTP requests.
        3)  The allowed client IP list contains the allowed IPs of the clients that can access the sensitiveUriList.
        4)  The allowedSessionCookie contains the session cookie name that confirms any valid HTTP request.
        5)  The customBlockPage contains the URL of the landing page for invalid HTTP requests.
