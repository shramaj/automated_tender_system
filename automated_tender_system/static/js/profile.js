/**
 * Created by mandeev on 31/3/17.
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

                    /*$("#edit").click(function () {
                                    $('#done').toggle();
                                    $(this).toggle();
                                    $('#np').eq(0).toggle();
                                    $('#cp').eq(0).toggle();
                                    $('#dd').eq(0).toggle();
                                          $('#done1').eq(0).toggle();
                                              $('#cancle1').eq(0).toggle();
                                });

                          $(function(){
                                 $('#edit').click(function(){
                                    $('.enableOnInput').prop('disabled', false);
                                        //$('#submitBtn').val('Update');
                                 });
                                });*/