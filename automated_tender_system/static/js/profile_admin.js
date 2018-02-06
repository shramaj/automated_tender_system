/**
 * Created by mandeev on 1/4/17.
 */


                    $(document).ready(function(){
                        $('#edit').on('click', function() {
                            if ( this.value === 'edit')
                            {
                                $("#updation").show();
                                $("#profile").hide();

                            }
                            else
                            {
                                $("#updation").hide();
                            }
                        });
                    });