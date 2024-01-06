# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os


bl_info = {
    "name": "SVG Import WIP",
    "author": "Jon McBride",
    "version": (1, 2),
    "blender": (3, 1, 2),
    "description": "Makes Importing and working with SVG's Easier",
    "warning": "Under Revision",
    "category": "Import-Export",
    "location": "View3D > Panel > SVG Tools",
}

###############################################
#    CUSTOM FUNCTIONS
###############################################

def getLocationDataOfObjects(objectList): # returns (xmin,ymin,zmin,xmax,ymax,zmax)
    objectsBound = [None,None,None,None,None,None] # (xmin,ymin,zmin,xmax,ymax,zmax)

    # Get Bounds
    for object in objectList:
        #Min Values
        if objectsBound[0]==None or objectsBound[0]>=object.bound_box[0][0]: objectsBound[0]=object.bound_box[0][0] #x
        if objectsBound[1]==None or objectsBound[1]>=object.bound_box[0][1]: objectsBound[1]=object.bound_box[0][1] #y
        if objectsBound[2]==None or objectsBound[2]>=object.bound_box[0][2]: objectsBound[2]=object.bound_box[0][2] #z
        #Max Values
        if objectsBound[3]==None or objectsBound[3]<=object.bound_box[6][0]: objectsBound[3]=object.bound_box[6][0] #x
        if objectsBound[4]==None or objectsBound[4]<=object.bound_box[6][1]: objectsBound[4]=object.bound_box[6][1] #y
        if objectsBound[5]==None or objectsBound[5]<=object.bound_box[6][2]: objectsBound[5]=object.bound_box[6][2] #z
    
    # Get Center
    centerVector = [(objectsBound[0]+objectsBound[3])/2,(objectsBound[1]+objectsBound[4])/2,(objectsBound[2]+objectsBound[5])/2 ]

    #Get Dimension
    objectsDimension = [abs(objectsBound[0]-objectsBound[3]),abs(objectsBound[1]-objectsBound[4]),abs(objectsBound[2]-objectsBound[5])]

    return {'bound':objectsBound, 'dimension':objectsDimension, 'center':centerVector };

def muliObjectOperation( objectList, function ):
    for object in objectList:
        if function:
            # Make active object
            bpy.ops.object.select_all(action='DESELECT') 
            object.select_set(True)
            bpy.context.view_layer.objects.active = object
            function(object)


###############################################
#    PROP UPDATE FUNCTIONS
###############################################
def svguiUpdateExtrude(self, context):
    # get selected objects
    selected = context.selected_objects
    print(self.svgiu_extrude)
    # itereatively extrude
    for object in selected:
        context.view_layer.objects.active = object
        context.object.data.extrude = self.svgiu_extrude

def svguiUpdateBevel_depth(self, context):
    # get selected objects
    selected = context.selected_objects
    # itereatively extrude
    for object in selected:
        context.view_layer.objects.active = object
        context.object.data.bevel_depth = self.svgiu_bevel_depth

def svguiUpdateBevel_resolution(self, context):
    # get selected objects
    selected = context.selected_objects
    # itereatively extrude
    for object in selected:
        context.view_layer.objects.active = object
        context.object.data.bevel_resolution = self.svgiu_bevel_resolution


    

###############################################
#    CUSTOM PROPERTIES
###############################################

bpy.types.Scene.svgiu_svgImportFilePath = bpy.props.StringProperty(
    name="", 
    default= "", 
    subtype='FILE_PATH') ;
bpy.types.Scene.svgiu_svgCentered = bpy.props.BoolProperty(
    name="Center Object Origin", 
    description="Set origin of all imported objects to center of imported svg objects", 
    default=True) ;
bpy.types.Scene.svgiu_svgLocation = bpy.props.FloatVectorProperty(
    name="SVG Location", 
    description="location of the imported svg", 
    subtype='XYZ',
    default=(0.0, 0.0, 0.0)) ;
bpy.types.Scene.svgiu_svgScale = bpy.props.FloatProperty(
    name="scale", 
    description="scale of the imported svg", 
    default=10) ;


bpy.types.Scene.svgiu_extrude = bpy.props.FloatProperty(
    name="Extrude Selected",
    update=svguiUpdateExtrude
    ) ;
bpy.types.Scene.svgiu_bevel_depth = bpy.props.FloatProperty(
    name="Depth",
    update=svguiUpdateBevel_depth
    ) ;
bpy.types.Scene.svgiu_bevel_resolution = bpy.props.IntProperty(
    name="Resolution",
    update=svguiUpdateBevel_resolution
    ) ;

###############################################
#    OPERATORS
###############################################

class SVGIU_OT_svgImportUtility( bpy.types.Operator ) :
    bl_idname = "scene.importsvg" ;
    bl_label = "Import SVG Utility" ;
    bl_options = {'REGISTER','UNDO'} ;

    #Operator Properties
    svgLocation = bpy.props.FloatVectorProperty(
        name="SVG Location",
        description="scale of the imported svg",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ');
    svgScale = bpy.props.FloatProperty(
        name="scale", 
        description="scale of the imported svg", 
        default=10) ;
    svgCentered = bpy.props.BoolProperty(
        name="Center Object Origin", 
        description="Set origin of all imported objects to center of imported svg objects", 
        default=True) ;
    
    @classmethod
    def poll( cls, context ) :
        return True ;
    
    def invoke( self, context, event ) :
        self.svgScale = bpy.context.scene.svgiu_svgScale
        self.svgLocation = bpy.context.scene.svgiu_svgLocation
        self.svgCentered = bpy.context.scene.svgiu_svgCentered
        return self.execute(context)
    
    def execute( self, context ) :
        svgLocation = self.svgLocation
        svgScale = self.svgScale
        svgCentered = self.svgCentered

        useGlobalUndo = context.preferences.edit.use_global_undo ;
        context.preferences.edit.use_global_undo = False ;
        try :
            filePath = bpy.context.scene.svgiu_svgImportFilePath

            if os.path.exists( filePath ) :
                filename, file_extension = os.path.splitext(filePath)
                if file_extension == '.svg' or file_extension == '.SVG':
                    #Get Imported Objects
                    oldObjects = set(bpy.data.objects) # document objects prior to import
                    bpy.ops.import_curve.svg(filepath=filePath)
                    importedObjects = set(bpy.data.objects)-oldObjects # document imported objects

                    objectsLocationData = getLocationDataOfObjects(importedObjects) # (xmin,ymin,zmin,xmax,ymax,zmax)
                    savedCursorLocation = bpy.context.scene.cursor.location
                    print(importedObjects)

                    bpy.ops.object.select_all(action='DESELECT') 
                    for object in importedObjects:
                        #Make Active Object
                        
                        object.select_set(True)
                        bpy.context.view_layer.objects.active = object

                        #Center Object Origin
                        if svgCentered == True:
                            bpy.context.scene.cursor.location = objectsLocationData['center']
                            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                            
                        #Import Location
                        object.location = (svgLocation[0],svgLocation[1],svgLocation[2])

                        #Scale Object
                        object.dimensions = (
                            svgScale*object.dimensions[0],
                            svgScale*object.dimensions[1],
                            svgScale*object.dimensions[2])
                        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                        #Scale bezier points - important for extrude operations
                        for spline in bpy.context.object.data.splines:
                            for point in spline.bezier_points:
                                point.radius = 1

                    bpy.context.scene.cursor.location = savedCursorLocation
                    object.users_collection[0].objects
                    
                else :
                    bpy.context.scene.svgiu_svgImportFilePath = "( WRONG FILETYPE )" ;              
            else :
                bpy.context.scene.svgiu_svgImportFilePath = "( WRONG FILEPATH )" ;
                print("LOG: Import SVG - FAILURE") ;
        finally :
            context.preferences.edit.use_global_undo = useGlobalUndo ;
            
            
        return {'FINISHED'} ;
    
class SVGIU_OT_svgEditUtility(  bpy.types.Operator ):
    print( "DO Something" )

###############################################
#    Panel
###############################################
        
class SVGIU_PT_svgImportUtilityPanel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport N Panel"""
    bl_label = "Import SVG"
    bl_idname = "SVG_IMPORT_UTILITY"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SVG Tools"

    def draw( self, context ) :
        
        layout = self.layout 
        layout.prop(context.scene, "svgiu_svgImportFilePath") 
        layout.prop(context.scene, "svgiu_svgCentered") 

        col = layout.column(align=True)
        col.prop(context.scene, "svgiu_svgLocation")
        
        layout.label( text='SVG Scale:')
        layout.prop(context.scene, "svgiu_svgScale")
        layout.operator( operator="scene.importsvg", text="Import SVG", icon='IMPORT' ) 

class SVGIU_PT_svgEditUtilityPanel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport N Panel"""
    bl_label = "Edit SVG"
    bl_idname = "SVG_EDIT_UTILITY"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SVG Tools"

    def draw( self, context ) :
        layout = self.layout 

        layout.prop(context.scene, "svgiu_extrude")

        col = layout.column(align=True)
        col.label( text="Bevel")
        col.prop(context.scene, "svgiu_bevel_depth")
        col.prop(context.scene, "svgiu_bevel_resolution")



classes = (
    SVGIU_OT_svgImportUtility,
    SVGIU_PT_svgImportUtilityPanel,
    SVGIU_PT_svgEditUtilityPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()