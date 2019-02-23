
Tool will support Export From Query and Spatial Export functionality.

User has to give either export query (-q) or spatial export (-x) parameters in command line argument.
Code is implemented to handle required parameters based on above parameters (-q or –x).

A. Export from Query 
########################
Example commandline for exporting 'Excel Production Workbook' for all the production unallocated entities defined by the 'ProdUnalloc_OK_Kingfisher' saved query.

The query has been created in Enerdeq Browser.
The export template is one of the standard export templates or oneline export templates.

IHS.EnergyWebServices.ExportFromQuerySample.exe -u YOURUSERNAME -p YOURPASSWORD -n "Excel Production Workbook (Excel 2007, 2010)" -t Oneline -q ProdUnalloc_OK_Kingfisher -m "North America" -v
IHS.EnergyWebServices.ExportFromQuerySample.exe -u YOURUSERNAME -p YOURPASSWORD -q UT-Conventional -m "Canada" -v
IHS.EnergyWebServices.ExportFromQuerySample.exe -u YOURUSERNAME -n "Excel Well Workbook (CSV)" -t "standard" -q "Last Activity Date" -f "Comma Separated" -d "Well" -l "https://webservices.ihsenergy.com/WebServices/" -m "North America" -v

B.	 Spatial Export
########################
	For spatial export following assumptions are made
		o	Default Spatial export layer is set to " " 
		o	Default Spatial format is set to "GEODATABASE_FILE"
		o	Default extent is set to “(-90,90), (-180,180)."
		o	Default overwrite is set to true
		o	User will be able to enter above values in command prompt by using the below 
			-x  : spatialExports
			-o : Spatial Format
			-e : Extent
			-w :working directory

o	Working directory is set to SpatialExport for SpatialExport and Export Query to ExportFromQuerySample under the configured temp directory
		Example: C:\Users\UserID\AppData\Local\Temp\SpatialExport
		start IHS.EnergyWebServices.ExportFromQuerySample.exe -u YOURUSERNAME -p YOURPASSWORD -x "Well Bore/Stick Path" -o "GEODATABASE_FILE" -e "(31.283,31.556)(-92.985,-92.575)"
		start IHS.EnergyWebServices.ExportFromQuerySample.exe -u YOURUSERNAME -p YOURPASSWORD -x "(45 Days) Upcoming Lease Sale Parcels - State" -o "GEODATABASE_FILE" -e "(31.283,31.556)(-92.985,-92.575)"
o	Spatial Exports layers can be given as comma separated string
		start IHS.EnergyWebServices.ExportFromQuerySample.exe  -u YOURUSERNAME -p YOURPASSWORD -x "Well Bore/Stick Path","Production Allocated","Activity - All","Well (Surface)" -e "(35.145290874,35.2625026)(-119.719871797,-119.589275365)"
o	Tool provides a facility run batch requests as well. 
	In order to do this create a batch file with the Spatial Export queries that needs to get executed and save the file with .bat extension. 
	Execute the executable file to run multiple commands define in the .bat file.
	
	**** NOTE: Pls. do not leave any white spaces while specifying the extent. 

C. Usage of Tile Size for Extended Exports
---------------------------------------------
Now that spatial exports are support within the ExportFromQuery tool we need to support extents beyond 3.6 x 3.6 degrees. 

When a request is larger than 3.6 by 3.6 then split the specified area into multiple tiles and loop through each.
Allow the user to specify the size of the tile, for example 2 by 2 or 3 by 3.

This will result in multiple zip file

In order to make use of this Tiles feature you can use the following commands:

(a) If changes are included in the App.config File
**************************************************
<add key="Username" value="" />
    <add key="Password" value="" />
    <add key="TemplateName" value="" />
    <add key="TemplateType" value="" />
    <add key="Query" value="" />
    <add key="LastUpdateDate" value="" />
    <add key="Datatype" value="" />
    <add key="FileType" value="" />
    <add key="Url" value="" />
    <add key="SpatialFormat" value="" />
    <add key="SpatialExtent" value="" />
    <add key="SpatialTileSize" value="2X2" />
    <add key="WorkingDirectory" value="" />
    <!-- in order to add multiple layers use:  -->
    <add key="SpatialExports" value="Well (Surface)" />
	
Example 1
*********
-u aa -p bb Allocated -e "(35.145290874,35.2625026)(-119.719871797,-119.589275365)" -t Oneline -v

Example 2
*********
-u aa -p bb -x  "Well (Surface)","Production Allocated" -e "(48.119,48.197)(-103.743,-102.118)" -v

Example 3
*********
-u aa -p bb -x  "Well (Surface)","Production Allocated" -e "(48.119,48.197)(-103.743,-102.118)" -v -i "1X1"

Example 4
*********
-u aa -p bb -x  "Well Bore/Stick Path","Production Allocated","Activity - All","Well (Surface)" -e "(35.145290874,35.2625026)(-119.719871797,-119.589275365)" -V -i "2X2"

Example 5
*********
-u aa -p bb -x  "Well Bore/Stick Path","Production Allocated","Activity - All","Well (Surface)" -e "(35.145290874,35.2625026)(-119.719871797,-119.589275365)" -V -i "2X2" -m "Canada"

C. Add XML TemplateName -n option
*********************************************************************8
You could parse XML in your template -n option by adding the xml in to your query as below. 
Note: You must have a valid query saved prior to this as the -q option is mandatory. 

Example 6
*********
IHS.EnergyWebServices.ExportFromQuerySample.exe  -u USERNAME -p PASSWORD -n "<EXPORT><TEXTUAL_EXPORTS><WELL_XML INCLUDE_IHS_TOPS='TRUE' INCLUDE_SUBSCRIBED_LATLONG_SOURCES='TRUE' INCLUDE_PRODFIT='TRUE'/></TEXTUAL_EXPORTS></EXPORT>" -q "Test_Export" -f "Comma Separated" -d "Well" -l "https://webservices.ihsenergy.com/WebServices/" -m "US" -v

Example 7 (with formatted XML)
*********
IHS.EnergyWebServices.ExportFromQuerySample.exe  -u USERNAME -p PASSWORD -n "<EXPORT>
	<TEXTUAL_EXPORTS>
		<WELL_XML INCLUDE_PRODFIT='TRUE'/>
	</TEXTUAL_EXPORTS>
</EXPORT>" -q "Test_Export" -f "Comma Separated" -d "Well" -l "https://webservices.ihsenergy.com/WebServices/" -m "US" -v


Additional Links
-------------------
IHS Energy Web Services Portal - https://webservicesportal.ihsenergy.com
	Developers Guide
	CriteriaXML Specification
	
Generate proxy class from a wsdl - http://msdn.microsoft.com/en-us/library/aa529578.aspx
Adding a web service reference - 

Disclaimers
-----------
All code samples are provided “as is” and are provided to demonstrate using the service operation in as simple a way as possible. They include elements of hard coding which should not be used in a production system. The samples do not include exception handling, which should be included in a production system. 
External links are provided throughout this document where relevant in order to provide helpful and useful information from the internet. IHS is not responsible for the content of external Internet sites.

