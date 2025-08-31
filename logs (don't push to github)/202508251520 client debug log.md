client debug:

COMPREHENSIVE DEBUG INFO

Form State:
• Company: 2e1218ac-d2a2-4213-90e7-4b222e5dbc4b
• Location: 1007JHWJ3169
• Location Display: San Francisco, California, US
• Is Anonymous: No
• Can Submit: Yes
Review Data:
• User Review Count: 0
• Last Review Date: N/A
• Review Categories: 8
• Rated Questions: 0/34
• Aggregate Rating: 0.00
Location Matching:
• Location Display: San Francisco, California, US
• City: San Francisco
• Country: US
• Matching Logic: User UUID + Company UUID + City + Country match
🔍 DEBUG - Review Matching Logic:
Total Reviews from API: 0 reviews found
Matching Method: User UUID + Company UUID + City + Country
Selected User ID: 2071f72c-dfc6-40a0-9b33-a8d1d1fa7026
Selected Company ID: 2e1218ac-d2a2-4213-90e7-4b222e5dbc4b
Selected City: San Francisco
Selected Country: US
Expected: Should find review with matching user+company+city+country
Console Check: Look for "Checking review match" logs
🔍 DEBUG - API Call Analysis:
API Endpoint: /api/reviews/?freight_forwarder_id=2e1218ac-d2a2-4213-90e7-4b222e5dbc4b
User ID: 2071f72c-dfc6-40a0-9b33-a8d1d1fa7026
Company ID: 2e1218ac-d2a2-4213-90e7-4b222e5dbc4b
API Response: 0 reviews returned
Issue: API is returning 0 reviews - check backend logs
Next Steps: Verify reviews exist in database for this company
🔍 DEBUG - Raw API Response Data:
API Response Status: Check console for detailed response data
Console Logs: Look for "Raw API Response" and "Response Structure Analysis"
Filtering Results: Look for "Filtering Results" logs
Expected: Backend returns 9 reviews, frontend should process them

Review table content:

user_id	freight_forwarder_id	city	country
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US
2071f72c-dfc6-40a0-9b33-a8d1d1fa7026	2e1218ac-d2a2-4213-90e7-4b222e5dbc4b	San Francisco	US